from pydantic import BaseModel
from typing import Optional, List, Dict, Any

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