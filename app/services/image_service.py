import asyncio
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
#import re
import boto3
import requests
import mimetypes
import os
from urllib.parse import urlparse
from app.services import image_service
from PIL import Image

load_dotenv()  # Load the .env file
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
bucket_name = "adventureappdms"

async def askDallE_structured(prompt: str, size: str):
    try:
        response = await asyncio.to_thread(
            client.images.generate,
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size=size, #Must be one of 1024x1024, 1792x1024, or 1024x1792
            style="vivid" # vivid or natural
        )
        return response
    except Exception as e:
        return f"Error: {e}"

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
)

def is_valid_image(url):
    """
    Checks if the URL points to a valid JPG or PNG image.
    
    :param url: Image URL.
    :return: Tuple (Boolean, File extension) - True if valid image, else False.
    """
    response = requests.head(url, allow_redirects=True)
    
    if response.status_code != 200:
        return False, None

    content_type = response.headers.get("Content-Type", "")
    if content_type in ["image/jpeg", "image/png"]:
        ext = ".jpg" if "jpeg" in content_type else ".png"
        return True, ext
    return False, None

def download_image(url):
    """
    Downloads an image from a URL.
    
    :param url: Image URL.
    :return: Tuple (image content, file extension).
    """
    response = requests.get(url, stream=True)
    
    if response.status_code != 200:
        raise Exception(f"Failed to download image: {response.status_code}")
    
    content_type = response.headers.get("Content-Type", "")
    ext = ".jpg" if "jpeg" in content_type else ".png"
    
    return response.content, ext

async def generate_presigned_url(bucket_name, object_key, expiration=3600):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_key},
        ExpiresIn=expiration
    )

async def upload_to_s3(image_data, bucket_name, file_name, ext):
    """
    Uploads image data to S3 and returns the public URL.
    
    :param image_data: Image file content.
    :param bucket_name: Name of the target S3 bucket.
    :param file_name: Name for the uploaded file.
    :param ext: File extension (e.g., .jpg, .png).
    :return: Public URL of the uploaded image.
    """
    s3_key = f"{file_name}{ext}"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=image_data,
            ContentType=mimetypes.types_map[ext]
        )
        presigned_url = await generate_presigned_url(bucket_name, s3_key, 3600)
    except Exception as e:
        return f"Error: {e}"

    print(presigned_url)    
    return {"bucket_name": bucket_name, "s3_key": s3_key, "presigned_url": presigned_url}

async def process_image(url):
    """
    Main function to validate, download, and upload an image to S3.
    
    :param url: URL of the image.
    :param bucket_name: Target S3 bucket.
    :return: Public URL of the uploaded image or error message.
    """
    valid, ext = is_valid_image(url)
    
    if not valid:
        return "Invalid image URL. Only JPG and PNG formats are supported."
    
    image_data, ext = download_image(url)
    
    file_name = os.path.basename(urlparse(url).path).split(".")[0]
    
    return await upload_to_s3(image_data, bucket_name, file_name, ext)



