from fastapi import FastAPI, HTTPException
import httpx
from typing import List

from .services.product_service import products_to_documents
from .models.schemas import Product


# Create a FastAPI instance
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

        
            documents = products_to_documents(products)

            
            return {"message": f" {documents} "}
    
    except httpx.HTTPError as e:
        # Raise an HTTPException so the client receives a 502 Bad Gateway
        raise HTTPException(status_code=502, detail=str(e))