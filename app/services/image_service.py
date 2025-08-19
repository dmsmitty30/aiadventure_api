import asyncio
import io
import mimetypes
import os
from urllib.parse import urlparse

# import re
import boto3
import requests
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel

from app.services import image_service

load_dotenv()  # Load the .env file
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
bucket_name = os.getenv("IMAGE_BUCKET_NAME")


async def askDallE_structured(prompt: str, size: str):
    try:
        response = await asyncio.to_thread(
            client.images.generate,
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size=size,  # Must be one of 1024x1024, 1792x1024, or 1024x1792
            style="vivid",  # vivid or natural
        )
        return response
    except Exception as e:
        return {"error": f"Failed to generate image with DALL-E: {str(e)}"}


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
        ExpiresIn=expiration,
    )


async def upload_to_s3(image_data, bucket_name, file_name, ext):
    """
    Uploads image data to S3 and returns the public URL.

    :param image_data: Image file content.
    :param bucket_name: Name of the target S3 bucket.
    :param file_name: Name for the uploaded file.
    :param ext: File extension (e.g., .jpg, .png).
    :return: Dictionary with bucket_name, s3_key, and presigned_url on success, or error dict on failure.
    """
    s3_key = f"{file_name}{ext}"

    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=image_data,
            ContentType=mimetypes.types_map[ext],
        )
        presigned_url = await generate_presigned_url(bucket_name, s3_key, 3600)
    except Exception as e:
        return {"error": f"Failed to upload to S3: {str(e)}"}

    print(presigned_url)
    return {
        "bucket_name": bucket_name,
        "s3_key": s3_key,
        "presigned_url": presigned_url,
    }


async def process_image(url, bucket_name=None):
    """
    Main function to validate, download, and upload an image to S3.

    :param url: URL of the image.
    :param bucket_name: Target S3 bucket. If None, uses the default from environment.
    :return: Dictionary with bucket_name, s3_key, and presigned_url on success, or error dict on failure.
    """
    if bucket_name is None:
        bucket_name = os.getenv("IMAGE_BUCKET_NAME")

    if not bucket_name:
        return {
            "error": "No bucket name provided and IMAGE_BUCKET_NAME not set in environment"
        }

    try:
        valid, ext = is_valid_image(url)

        if not valid:
            return {
                "error": "Invalid image URL. Only JPG and PNG formats are supported."
            }

        image_data, ext = download_image(url)

        file_name = os.path.basename(urlparse(url).path).split(".")[0]

        result = await upload_to_s3(image_data, bucket_name, file_name, ext)

        # Check if upload_to_s3 returned an error
        if isinstance(result, dict) and "error" in result:
            return result

        return result
    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}


async def create_thumbnail(
    image_data, width, height, crop_position="center", quality=85
):
    """
    Creates a cropped and scaled thumbnail from image data.

    :param image_data: Raw image data (bytes)
    :param width: Target width
    :param height: Target height
    :param crop_position: Where to crop from ("center", "top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right")
    :param quality: JPEG quality (1-100)
    :return: Processed image data as bytes
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGB if necessary (for JPEG output)
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")

        # Calculate crop dimensions
        img_width, img_height = image.size
        target_ratio = width / height
        img_ratio = img_width / img_height

        if target_ratio > img_ratio:
            # Target is wider than image, crop height
            new_height = int(img_width / target_ratio)
            new_width = img_width
        else:
            # Target is taller than image, crop width
            new_width = int(img_height * target_ratio)
            new_height = img_height

        # Calculate crop box based on position
        left = 0
        top = 0

        if crop_position == "center":
            left = (img_width - new_width) // 2
            top = (img_height - new_height) // 2
        elif crop_position == "top":
            left = (img_width - new_width) // 2
            top = 0
        elif crop_position == "bottom":
            left = (img_width - new_width) // 2
            top = img_height - new_height
        elif crop_position == "left":
            left = 0
            top = (img_height - new_height) // 2
        elif crop_position == "right":
            left = img_width - new_width
            top = (img_height - new_height) // 2
        elif crop_position == "top-left":
            left = 0
            top = 0
        elif crop_position == "top-right":
            left = img_width - new_width
            top = 0
        elif crop_position == "bottom-left":
            left = 0
            top = img_height - new_height
        elif crop_position == "bottom-right":
            left = img_width - new_width
            top = img_height - new_height

        # Crop the image
        cropped_image = image.crop((left, top, left + new_width, top + new_height))

        # Resize to target dimensions
        resized_image = cropped_image.resize((width, height), Image.Resampling.LANCZOS)

        # Convert to bytes
        output_buffer = io.BytesIO()
        resized_image.save(output_buffer, format="JPEG", quality=quality, optimize=True)
        output_buffer.seek(0)

        return output_buffer.getvalue()

    except Exception as e:
        raise Exception(f"Failed to create thumbnail: {str(e)}")


async def process_thumbnail_from_s3(
    bucket_name,
    s3_key,
    width,
    height,
    crop_position="center",
    quality=85,
    use_cache=True,
):
    """
    Downloads an image from S3, processes it into a thumbnail, and returns the processed image data.
    Optionally caches the result for future use.

    :param bucket_name: S3 bucket name
    :param s3_key: S3 object key
    :param width: Target width
    :param height: Target height
    :param crop_position: Crop position
    :param quality: JPEG quality
    :param use_cache: Whether to use caching
    :return: Processed thumbnail image data as bytes
    """
    try:
        if use_cache:
            # Generate cache key
            cache_key = generate_thumbnail_cache_key(
                s3_key, width, height, crop_position, quality
            )

            # Check if cached version exists
            if await get_cached_thumbnail(bucket_name, cache_key):
                # Return cached version
                response = s3_client.get_object(Bucket=bucket_name, Key=cache_key)
                return response["Body"].read()

        # Download original image from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        image_data = response["Body"].read()

        # Create thumbnail
        thumbnail_data = await create_thumbnail(
            image_data, width, height, crop_position, quality
        )

        # Cache the result if caching is enabled
        if use_cache:
            await upload_thumbnail_to_cache(bucket_name, cache_key, thumbnail_data)

        return thumbnail_data

    except Exception as e:
        raise Exception(f"Failed to process thumbnail from S3: {str(e)}")


def generate_thumbnail_cache_key(s3_key, width, height, crop_position, quality):
    """
    Generates a cache key for a thumbnail based on its parameters.

    :param s3_key: Original S3 object key
    :param width: Target width
    :param height: Target height
    :param crop_position: Crop position
    :param quality: JPEG quality
    :return: Cache key string
    """
    # Remove file extension from original key
    base_key = os.path.splitext(s3_key)[0]

    # Create cache key with parameters
    cache_key = f"{base_key}_thumb_{width}x{height}_{crop_position}_q{quality}.jpg"

    return cache_key


async def get_cached_thumbnail(bucket_name, cache_key):
    """
    Checks if a cached thumbnail exists and returns it if found.

    :param bucket_name: S3 bucket name
    :param cache_key: Cache key for the thumbnail
    :return: Thumbnail data if found, None otherwise
    """
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=cache_key)
        return True  # Thumbnail exists
    except s3_client.exceptions.NoSuchKey:
        return False  # Thumbnail doesn't exist
    except Exception:
        return False  # Error occurred, assume no thumbnail


async def upload_thumbnail_to_cache(bucket_name, cache_key, thumbnail_data):
    """
    Uploads a processed thumbnail to S3 cache.

    :param bucket_name: S3 bucket name
    :param cache_key: Cache key for the thumbnail
    :param thumbnail_data: Processed thumbnail image data
    :return: True if successful, False otherwise
    """
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=cache_key,
            Body=thumbnail_data,
            ContentType="image/jpeg",
            CacheControl="public, max-age=86400",  # Cache for 24 hours
        )
        return True
    except Exception:
        return False
