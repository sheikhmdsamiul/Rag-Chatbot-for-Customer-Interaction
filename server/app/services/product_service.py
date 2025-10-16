from langchain.schema import Document
from typing import List
import json

from ..models.schemas import Product

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