from fastapi import FastAPI, HTTPException
import httpx

from .services.product_service import products_to_documents
from .services.chatbot_service import rag_chat
from .core.chat_state import chat_state
from .models.schemas import Product, ChatRequest, ChatResponse

from langchain_core.messages import HumanMessage, AIMessage


#Create a FastAPI instance
app = FastAPI()


#Fetch data 
@app.get("/api/products")
async def fetch_data():
    url = "https://dummyjson.com/products"

    try:

        #Make an asynchronous HTTP GET request to fetch product data
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        #Parse products and convert to documents
        products = [Product(**product_data) for product_data in data.get("products", [])]

        # Update global chat state with documents
        chat_state["documents"] = products_to_documents(products)


        return {
                "message": "Products fetched and stored in memory.",
                "total_products": len(products)
                }
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))
    


#Endpoint for RAG chat with the given query and context.
@app.post("/api/chat", response_model = ChatResponse)
async def rag_chat_endpoint(request: ChatRequest):

    chat_history = chat_state["chat_history"]
    documents = chat_state["documents"]

    try:

        user_query = request.query.strip() if request.query else None
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        #Add user message to history
        chat_history.append(HumanMessage(content=user_query))

        #Get RAG response with combined input
        response = rag_chat(user_query, chat_history, documents)

        
        if response:

            #Convert history to JSON-safe format
            history_json = [{"role": msg.type, "content": msg.content} for msg in chat_history]

            #Add AI response to history
            chat_history.append(AIMessage(content=response))

            return {"chat_history": history_json, "response": response}
        
        else:
            raise HTTPException(status_code=500, detail="No response generated")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chatbot: {str(e)}")