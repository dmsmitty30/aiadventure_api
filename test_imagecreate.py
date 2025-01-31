import asyncio
import os
from app.database import get_adventure_by_id
from app.services.image_service import process_image, askDallE_structured
# Load environment variables

bucket_name = "adventureappdms"
async def test():
    adventure_id="6776f9d029fb9e8520c45e61"
    adventure = await get_adventure_by_id(adventure_id)

    prompt = f"Create a title image for a book titled '{adventure['title']}'. The style should mimic a 70's or 80's adventure novel. It should be an image only - no text, borders, or other content. The book synopsis is as follows:\n\n{adventure['synopsis']}"
    
    response = await askDallE_structured(prompt,"1024x1024")
    image_url = response.data[0].url
    print(image_url)

async def test_process():
    adventure_id="6798822e7139421b8d9c55fd"
    adventure = await get_adventure_by_id(adventure_id)

    prompt = f"Create a title image for a book titled '{adventure['title']}'. The style should mimic a 70's or 80's adventure novel. It should be an image only - no text, borders, or other content. The book synopsis is as follows:\n\n{adventure['synopsis']}"
    
    response = await askDallE_structured(prompt,"1024x1792")

    
    image_url = response.data[0].url
    uploaded_image = await process_image(image_url, bucket_name)
    print(uploaded_image)



asyncio.run(test_process())
    