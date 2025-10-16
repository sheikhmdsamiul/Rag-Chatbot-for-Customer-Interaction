from langchain_core.messages import AIMessage

#Global memory for one chatbot instance
chat_state = {
    "chat_history": [AIMessage(content="Hi! I'm your product assistant. How can I help you today?")],
    "documents": []
}