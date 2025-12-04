from pydantic import BaseModel, Field
from pprint import pprint
from typing import Optional, List

from src.utils.ollama_llm import OllamaLLM

class ProductReview(BaseModel):
    product_name: str = Field(..., description="Name of the product being reviewed")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    reviewer_name: str = Field(..., description="Name of the person writing the review")
    review_text: str = Field(..., description="The actual review content")
    pros: List[str] = Field(default_factory=list, description="Positive aspects mentioned")
    cons: List[str] = Field(default_factory=list, description="Negative aspects mentioned")
    would_recommend: bool = Field(..., description="Whether the reviewer would recommend this product")
    verified_purchase: Optional[bool] = Field(None, description="Whether this is a verified purchase")

SAMPLE = """
Review by: John Smith

I bought the UltraSound Bluetooth Speaker last month and I'm really impressed! 
The sound quality is crystal clear and the bass is amazing. Battery life easily 
lasts 12+ hours which is perfect for outdoor parties. 

The only downside is that it's a bit heavy to carry around, and the price is 
slightly higher than competitors. But overall, the quality justifies the cost.

I'd definitely recommend this to anyone looking for a premium speaker.

Rating: 4 out of 5 stars
Verified Purchase: Yes
"""

def main():
    llm = OllamaLLM.connect_to_ollama_cloud()
    response = llm.ask_w_structured_output(SAMPLE, ProductReview)
    pprint(response.model_dump(mode="python"))


if __name__ == "__main__":
    main()
