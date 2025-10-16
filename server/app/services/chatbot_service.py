import os
import logging
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

#Configuration 
MODEL = os.environ.get("RAG_MODEL", "llama-3.3-70b-versatile")
RE_RANKING_MODEL = os.environ.get("RE_RANKING_MODEL", "BAAI/bge-reranker-base")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

#Module-level placeholders for lazy initialization
llm = None
embeddings = None

logger = logging.getLogger(__name__)


def init_models():
    """Initialize LLM and embeddings lazily. Safe to call multiple times."""
    global llm, embeddings
    # Initialize embeddings first 
    if embeddings is None:
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        except Exception as e:
            logger.error("Failed to initialize embeddings: %s", e)
            raise RuntimeError("Embeddings initialization failed. Ensure 'langchain_huggingface' is installed and the embedding model name is valid.")

    # Initialize LLM only if GROQ_API_KEY is available (LLM is optional at import-time)
    if llm is None:
        try:
            from langchain_groq import ChatGroq
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if groq_api_key:
                llm = ChatGroq(groq_api_key=groq_api_key, model=MODEL, temperature=0.1)
            else:
                logger.warning("GROQ_API_KEY not set; LLM will remain uninitialized until a key is provided.")
        except Exception as e:
            # LLM is optional for initializing embeddings; log and continue
            logger.warning("Optional LLM library not available or failed to initialize: %s", e)

def get_vector_store(documents):
    """ Create and return a vector store for the documents
    Args:
        documents (list): A list of documents to be indexed in the vector store.
    Returns:
        FAISS: A FAISS vector store containing the indexed documents."""
    
    try:
        # Ensure embeddings are initialized
        if embeddings is None:
            init_models()

        # Create a FAISS vector store from the chunks
        vector_store = FAISS.from_documents(documents, embeddings)

        return vector_store
    
    except Exception as e:
        raise ValueError(f"Error creating vector store: {str(e)}")
    

    

# Function to run RAG chat with the given query and context
# This function uses the vector store to retrieve relevant documents and answer the query.
def rag_chat(query, chat_history,documents):
    """Run RAG chat with the given query and context.
    Args:
        query (str): The user query to answer.
        chat_history (list): The chat history to provide context.
        documents (list): The langchain documents to get vector stored.
    Returns:
        str: The answer to the query."""
    
    if not query:
        return "Query cannot be empty."
    
    # Ensure models/embeddings are initialized. This will initialize embeddings and try to initialize the LLM.
    try:
        init_models()
    except Exception as e:
        # Bubble up a clear runtime error
        raise RuntimeError(f"Model initialization failed: {e}")

    # Creating vector store and retriever
    vector_store = get_vector_store(documents)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Contextualization prompt 
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given a chat history and the latest user question, "
                   "reformulate the question so it is standalone. Do NOT answer it."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    

    # History-aware retriever for contextualizing the query
    # This retriever uses the chat history to provide context for the query
    history_aware_retriever = create_history_aware_retriever(
        llm = llm,
        retriever = retriever,
        prompt = contextualize_prompt
    )
    

    # question answer prompt
    qa_prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are a product information assistant powered by a retrieval-augmented system.

            Your goal is to help users by accurately answering questions about products, their features, categories, prices, or descriptions.

            You have access to a set of retrieved context documents that contain product details.

            Follow these rules carefully:

            1. Base every answer ONLY on the retrieved context. If the context does not contain the information, respond with:
            "I'm sorry, I couldn’t find that information in the available product data."

            2. Always prefer factual, concise, and human-friendly answers.
            Avoid guessing, assuming, or fabricating any product details.

            3. Use markdown for clarity and structure.

            4. When possible, include relevant fields such as:
            - **Name**: [Product name]
            - **Description**: [Short summary]
            - **Category**: [Product category]
            - **Price**: [Price if available]
            - **Rating**: [Rating if provided]

            5. If the user asks for comparisons or recommendations, reference facts from the retrieved data rather than making subjective claims.

            6. Format your final output as follows:

            **Answer:** [Your direct, helpful response]

            7. If user asks for source, always provide cite the source as shown with the answer format mentioned in rule 6.:

            **Supporting Context:** "[Quote or summary of key retrieved text]"

            **Source:** [Product name or section title]

            Only output this information — do not include any reasoning or extra commentary.
            """

            "{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])

  
    #Question answer chain
    #This chain uses the LLM to answer the question based on the retrieved context
    #It combines the chat history and the context to generate a response
    qa_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=qa_prompt_template     
    )

    # Retrieval chain 
    # This chain combines the history-aware retriever and the question answer chain to provide a complete RAG chat experience
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        qa_chain
    )

    # Invoke the RAG chain with the query and chat history
    # This will return the answer to the query based on the context and chat history
    answer = rag_chain.invoke({
        "input": query,
        "chat_history": chat_history
    })
    
    return answer["answer"]


