import json
from datetime import datetime
from typing import Annotated

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.security import OAuth2PasswordBearer

import app.services.user_service as us
from app.database import (delete_adventure, get_adventure_by_id,
                          get_adventure_collection, truncate_adventure,
                          update_adventure_nodes)
from app.schemas.adventure import (AdventureBase, AdventureCreate,
                                   AdventureDelete, AdventureList,
                                   AdventureNodes, AdventureResponse,
                                   AdventureTruncate, NodeCreate)
from app.schemas.image import ImageResponse
from app.services.adventure_service import (fetch_adventures,
                                            generate_new_node,
                                            generate_new_story,
                                            get_adventure_for_user)
from app.services.image_service import (askDallE_structured,
                                        generate_presigned_url, process_image,
                                        process_thumbnail_from_s3)
from app.services.user_service import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/list", response_model=AdventureList)
async def adventure_list(token: Annotated[str, Depends(oauth2_scheme)]):
    print(f"TOKEN: {token}")
    owner_id = us.decode_access_token(token)
    print(f"OWNER:{owner_id}")
    response = await fetch_adventures(owner_id)
    print(f"RESPONSE {response}")
    response_array = []
    if len(response) > 0:
        for a in response:
            response_array.append(
                {
                    "adventure_id": a["id"],
                    "title": a["title"],
                    "synopsis": a["synopsis"],
                    "userPrompt": "",
                    "createdAt": a["createdAt"],
                    "perspective": a["perspective"],
                    "max_levels": a["max_levels"],
                    "min_words_per_level": a["min_words_per_level"],
                    "max_words_per_level": a["max_words_per_level"],
                    "numNodes   ": a["numNodes"],
                }
            )
    print("RETURNING!!!")
    return {"adventures": response_array}


@router.get("/nodes/{adventure_id}", response_model=AdventureNodes)
async def adventure_nodes(
    adventure_id: str, token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure_id, user_id)

    if response == 401:
        raise HTTPException(status_code=401, detail="Content Not authorized for user")
    if response == 404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    nodes = response["nodes"]
    return {"adventure_id": str(response["_id"]), "nodes": nodes}


@router.post("/start", response_model=AdventureResponse)
async def start_adventure(
    adventure: AdventureCreate, token: Annotated[str, Depends(oauth2_scheme)]
):
    """Starts a new adventure."""
    user_id = us.decode_access_token(token)
    # Generate story structure
    prompt = adventure.prompt
    max_levels = adventure.max_levels
    min_words_per_level = adventure.min_words_per_level
    max_words_per_level = adventure.max_words_per_level
    perspective = adventure.perspective.value
    coverimage = adventure.coverimage

    # print(prompt)
    # Generate story
    new_story_json = await generate_new_story(
        prompt, perspective, min_words_per_level, max_words_per_level
    )
    new_story = json.loads(new_story_json)
    # Create story structure
    i = 0

    # Initialize image-related variables
    image_bucket_name = None
    image_s3_key = None

    # Generate a cover image for the story and upload it to S3 if requested:
    if coverimage:
        new_image = await askDallE_structured(prompt, "1024x1792")
        if isinstance(new_image, dict) and "error" in new_image:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image: {new_image['error']}",
            )

        image_url = new_image.data[
            0
        ].url  # This is a temporary ChatGPT URL. Expires in 60 minutes.
        s3_image_details = await process_image(image_url)

        if isinstance(s3_image_details, dict) and "error" in s3_image_details:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process image: {s3_image_details['error']}",
            )

        image_bucket_name = s3_image_details["bucket_name"]
        image_s3_key = s3_image_details["s3_key"]

    options = new_story.get("options")
    createdAt = datetime.utcnow()
    adventure = {
        "owner_id": user_id,
        "title": new_story["title"],
        "synopsis": new_story["synopsis"],
        "userPrompt": prompt,
        "createdAt": createdAt,
        "perspective": perspective,
        "max_levels": max_levels,
        "min_words_per_level": min_words_per_level,
        "max_words_per_level": max_words_per_level,
        "nodes": [],
    }

    # Add image fields only if a cover image was generated
    if coverimage and image_bucket_name and image_s3_key:
        adventure["image_s3_bucket"] = image_bucket_name
        adventure["image_s3_key"] = image_s3_key

    # Save to database
    adventure_collection = get_adventure_collection()
    result = await adventure_collection.insert_one(adventure)

    node = {
        "createdAt": createdAt,
        "prev_option_index": None,
        "prev_option_text": None,
        "text": new_story["text"],
        "options": new_story["options"],
    }

    # Append Node to story
    node_result = await update_adventure_nodes(str(result.inserted_id), node)

    # Prepare response
    response_data = {
        "adventure_id": str(result.inserted_id),
        "title": new_story["title"],
        "synopsis": new_story["synopsis"],
        "createdAt": createdAt,
    }

    # Add cover image URL only if a cover image was generated
    if coverimage and image_bucket_name and image_s3_key:
        image_url = await generate_presigned_url(
            image_bucket_name, image_s3_key, expiration=3600
        )
        response_data["coverImageURL"] = image_url

    return response_data
    # response = RedirectResponse(url="/", status_code=303)
    # return(response)


@router.put("/continue", response_model=AdventureResponse)
async def continue_adventure(
    adventure: NodeCreate, token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure.adventure_id, user_id)
    print(response)
    if response == 401:
        raise HTTPException(status_code=401, detail="Content Not authorized for user")
    if response == 404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if (
        len(response["nodes"]) < adventure.start_from_node_id + 1
        or adventure.start_from_node_id < 0
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Bad Request: Adventure Node {adventure.start_from_node_id} out of range.",
        )
    if (
        len(response["nodes"][adventure.start_from_node_id]["options"])
        < adventure.selected_option + 1
        or adventure.selected_option < 0
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Bad Request: Option {adventure.selected_option} does not exist.",
        )

    start_from_node_id = adventure.start_from_node_id
    # print("startfrom: "+str(start_from_node_id))
    # print("starting from:"+str(start_from_node_id))

    node = await generate_new_node(
        adventure.adventure_id,
        start_from_node_id,
        adventure.selected_option,
        adventure.end_after_insert,
    )
    node["prev_option_index"] = adventure.selected_option

    # Generate New Story Node from specified Node.

    result = await update_adventure_nodes(adventure.adventure_id, node)
    new_node_index = start_from_node_id + 1
    return {"adventure_id": adventure.adventure_id, "node_index": new_node_index}
    # response = RedirectResponse(url="/adventure/{adventure_id}/{new_node_index}")
    # return(response)


@router.delete("/delete", response_model=AdventureResponse)
async def adventure_delete(
    adventure: AdventureDelete, token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure.adventure_id, user_id)
    if response == 404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if response == 401 or us.decode_access_token(token) != response["owner_id"]:
        raise HTTPException(
            status_code=401, detail="User not authorized to delete this content."
        )

    response = await delete_adventure(adventure.adventure_id)
    return {"action": "deleteAdventure", "adventure_id": adventure.adventure_id}


@router.patch("/truncate", response_model=AdventureResponse)
async def adventure_truncate(
    adventure: AdventureTruncate, token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure.adventure_id, user_id)
    if response == 404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if response == 401 or us.decode_access_token(token) != response["owner_id"]:
        raise HTTPException(
            status_code=401, detail="User not authorized to truncate this content."
        )
    response = await truncate_adventure(adventure.adventure_id, adventure.node_index)
    return {
        "action": "truncatedAdventure",
        "adventure_id": adventure.adventure_id,
    }


@router.put("/coverImage/update/{adventure_id}", response_model=ImageResponse)
async def create_or_update_cover_image(
    adventure_id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    force_regenerate: bool = False,
    custom_prompt: str = None,
):
    """Create or update a cover image for an existing adventure."""
    user_id = us.decode_access_token(token)

    # Get the adventure and verify user ownership
    response = await get_adventure_for_user(adventure_id, user_id)
    if response == 404:
        raise HTTPException(status_code=404, detail="Adventure not found")
    if response == 401:
        raise HTTPException(status_code=401, detail="Content not authorized for user")

    # Check if adventure already has a cover image
    has_existing_image = "image_s3_bucket" in response and "image_s3_key" in response

    if has_existing_image and not force_regenerate:
        # If image exists and user doesn't want to force regenerate, return existing image URL
        url = await generate_presigned_url(
            response["image_s3_bucket"], response["image_s3_key"], expiration=3600
        )
        return {"presigned_url": url}

    # Determine which prompt to use for image generation
    prompt = custom_prompt if custom_prompt else response.get("userPrompt", "")
    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="No prompt available for image generation. Please provide a custom_prompt or ensure the adventure has a userPrompt.",
        )

    # Generate new image with DALL-E
    new_image = await askDallE_structured(prompt, "1024x1792")
    if isinstance(new_image, dict) and "error" in new_image:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate image: {new_image['error']}"
        )

    image_url = new_image.data[0].url
    s3_image_details = await process_image(image_url)

    if isinstance(s3_image_details, dict) and "error" in s3_image_details:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {s3_image_details['error']}",
        )

    # Update the adventure with new image details
    adventure_collection = get_adventure_collection()
    update_result = await adventure_collection.update_one(
        {"_id": ObjectId(adventure_id)},
        {
            "$set": {
                "image_s3_bucket": s3_image_details["bucket_name"],
                "image_s3_key": s3_image_details["s3_key"],
            }
        },
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=500, detail="Failed to update adventure with new image details"
        )

    # Generate presigned URL for the new image
    presigned_url = await generate_presigned_url(
        s3_image_details["bucket_name"], s3_image_details["s3_key"], expiration=3600
    )

    return {"presigned_url": presigned_url}


"""
@router.put("/regenerateCoverImageURL", response_model=ImageResponse)
async def adventure_cover(adventure: AdventureBase, token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure_id, user_id)
    if response==404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if response==401 or us.decode_access_token(token) != response["owner_id"]:
        raise HTTPException(status_code=401, detail="User not authorized to delete this content.")

    new_image = await askDallE_structured(prompt,"1024x1792")    
    image_url = new_image.data[0].url # This is a temporary ChatGPT URL. Expires in 60 minutes.
    s3_image_details = await process_image(image_url)


    url = await generate_presigned_url(response["image_s3_bucket"], response["image_s3_key"], expiration=3600)
    return {"presigned_url": url}
"""


@router.get("/coverImage/{adventure_id}")
async def get_cover_image_thumbnail(
    adventure_id: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    width: int = 300,
    height: int = 200,
    crop: str = "center",  # center, top, bottom, left, right, top-left, top-right, bottom-left, bottom-right
    quality: int = 85,
    use_cache: bool = True,
):
    """Get a cropped and scaled version of the adventure's cover image for thumbnails/previews."""
    user_id = us.decode_access_token(token)

    # Get the adventure and verify user ownership
    response = await get_adventure_for_user(adventure_id, user_id)
    if response == 404:
        raise HTTPException(status_code=404, detail="Adventure not found")
    if response == 401:
        raise HTTPException(status_code=404, detail="Content not authorized for user")

    # Check if the adventure has a cover image
    if "image_s3_bucket" not in response or "image_s3_key" not in response:
        raise HTTPException(
            status_code=404, detail="This adventure does not have a cover image"
        )

    # Validate parameters
    if width <= 0 or height <= 0:
        raise HTTPException(
            status_code=400, detail="Width and height must be positive integers"
        )
    if width > 2000 or height > 2000:
        raise HTTPException(
            status_code=400, detail="Width and height cannot exceed 2000 pixels"
        )
    if quality < 1 or quality > 100:
        raise HTTPException(status_code=400, detail="Quality must be between 1 and 100")

    # Validate crop position
    valid_crop_positions = [
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ]
    if crop not in valid_crop_positions:
        raise HTTPException(
            status_code=400,
            detail=f"Crop position must be one of: {', '.join(valid_crop_positions)}",
        )

    try:
        # Process the thumbnail
        thumbnail_data = await process_thumbnail_from_s3(
            response["image_s3_bucket"],
            response["image_s3_key"],
            width,
            height,
            crop,
            quality,
            use_cache,
        )

        # Return the processed thumbnail image
        return Response(
            content=thumbnail_data,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Disposition": f"inline; filename=thumbnail_{width}x{height}.jpg",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process thumbnail: {str(e)}"
        )
