from pydantic import BaseModel, Field
from pprint import pprint
from typing import Optional, List, Literal
from pathlib import Path

from OllamaStructured import OllamaLLM

class ProductReview(BaseModel):
    product_name: str = Field(..., description="Name of the product being reviewed")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    reviewer_name: str = Field(..., description="Name of the person writing the review")
    review_text: str = Field(..., description="The actual review content")
    pros: List[str] = Field(default_factory=list, description="Positive aspects mentioned")
    cons: List[str] = Field(default_factory=list, description="Negative aspects mentioned")
    would_recommend: bool = Field(..., description="Whether the reviewer would recommend this product")
    verified_purchase: Optional[bool] = Field(None, description="Whether this is a verified purchase")

class ImageReview(BaseModel):
    gender: Literal['male', 'female'] = Field(..., description="Gender of the person in the image")
    age: int = Field(..., ge=1, le=100, description="Age of the person in the image")
    ethnicity: Literal['white', 'black', 'asian', 'other'] = Field(..., description="Ethnicity of the person in the image")
    background: str = Field(..., description="Background of the person in the image")
    mood: Literal['happy', 'sad', 'angry', 'neutral'] = Field(..., description="Mood of the person in the image")    

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

SAMPLE_IMAGE = Path('/Users/ozgunyargi/Documents/SU/PHD Application/Profile_Photo.jpg')

def text_sample():
    llm = OllamaLLM.connect_to_ollama_cloud()
    response = llm.ask_w_structured_output(SAMPLE, ProductReview)
    pprint(response.model_dump(mode="python"))

def image_sample():
    llm = OllamaLLM.connect_to_ollama_cloud(
        model='qwen3-vl:235b-cloud'
    )
    response = llm.ask_w_structured_output("Define the image", ImageReview, SAMPLE_IMAGE.read_bytes(),)
    pprint(response.model_dump(mode="python"))

if __name__ == "__main__":
    image_sample()
