from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import httpx
from langchain.schema import Document
from typing import List, Optional, Dict, Any
import json


# Create a FastAPI instance
app = FastAPI()

#Define Product Model
class Product(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    discountPercentage: Optional[float] = None
    rating: Optional[float] = None
    stock: Optional[int] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    weight: Optional[int] = None
    thumbnail: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    dimensions: Optional[Dict[str, Any]] = None
    warrantyInformation: Optional[str] = None
    shippingInformation: Optional[str] = None
    availabilityStatus: Optional[str] = None
    reviews: Optional[List[Dict[str, Any]]] = None
    returnPolicy: Optional[str] = None
    minimumOrderQuantity: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None



#Convert Products to LangChain Documents
def products_to_documents(products: List[Product]) -> List[Document]:
    docs = []

    #Process each product individually
    for product in products:
        #Convert the entire product to a plain dict
        product_dict = product.dict()

        #Create a full JSON snapshot for completeness
        json_content = json.dumps(product_dict, indent=2, ensure_ascii=False)

        #Create a natural language summary for better embedding quality
        summary_parts = [
            f"Product Title: {product.title}",
            f"Description: {product.description}",
            f"Category: {product.category}",
            f"Brand: {product.brand or 'N/A'}",
            f"Price: ${product.price}",
            f"Discount: {product.discountPercentage or 0}%",
            f"Rating: {product.rating or 'N/A'}",
            f"Stock: {product.stock or 'Unknown'}",
        ]

        #Add optional fields if they exist
        if product.tags:
            summary_parts.append(f"Tags: {', '.join(product.tags)}")

        if product.reviews:
            summary_parts.append(f"Total Reviews: {len(product.reviews)}")

        summary_text = "\n".join(summary_parts)

        #ombine the summary + raw JSON for full information retention
        combined_content = (
            "=== PRODUCT SUMMARY ===\n"
            + summary_text
            + "\n\n=== FULL PRODUCT JSON ===\n"
            + json_content
        )

        #Store original data in metadata as JSON
        metadata = {
            "id": product.id,
            "title": product.title,
            "category": product.category,
            "brand": product.brand,
            "price": product.price,
            "raw_data_json": json_content  
        }

        #Create LangChain Document
        docs.append(Document(page_content=combined_content, metadata=metadata))

    return docs

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

        # Parse products and convert to documents
        products = [Product(**product_data) for product_data in data["products"]]
        documents = products_to_documents(products)

        return {"message": f" {documents} "}
    
    except httpx.HTTPError as e:
        return {"error": str(e)}