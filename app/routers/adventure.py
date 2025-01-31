from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from app.database import get_adventure_collection, get_adventure_by_id, update_adventure_nodes, delete_adventure, truncate_adventure
from app.services.adventure_service import generate_new_story, generate_new_node, fetch_adventures, get_adventure_for_user
from app.services.user_service import get_current_user
from app.services.image_service import askDallE_structured, process_image, generate_presigned_url
from app.schemas.adventure import AdventureBase, AdventureList, AdventureNodes, AdventureCreate, AdventureResponse, NodeCreate, AdventureDelete, AdventureTruncate
from app.schemas.image import ImageResponse
from bson.objectid import ObjectId
import app.services.user_service as us
from datetime import datetime
import json

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/list", response_model=AdventureList)
async def adventure_list(token: Annotated[str, Depends(oauth2_scheme)]):
    print(f"TOKEN: {token}")
    owner_id = us.decode_access_token(token)
    print(f"OWNER:{owner_id}")
    response = await fetch_adventures(owner_id)
    print(f"RESPONSE {response}")
    response_array=[]
    if len(response)>0:
        for a in response:
            response_array.append({
                "adventure_id":a['id'],
                "title":a['title'],
                "synopsis":a['synopsis'],
                "userPrompt":"",
                "createdAt":a['createdAt'],
                "perspective":a['perspective'],
                "max_levels":a['max_levels'],
                "min_words_per_level":a['min_words_per_level'],
                "max_words_per_level":a['max_words_per_level'],
                "numNodes   ":a['numNodes']
                })
    print("RETURNING!!!")
    return {"adventures": response_array}

@router.get("/nodes/{adventure_id}", response_model=AdventureNodes)
async def adventure_nodes(adventure_id: str, token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure_id, user_id)
    
    if response==401:
        raise HTTPException(status_code=401, detail="Content Not authorized for user")
    if response==404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    nodes = response['nodes']
    return {"adventure_id":str(response['_id']), "nodes":nodes}

@router.post("/start", response_model=AdventureResponse)
async def start_adventure(adventure: AdventureCreate, token: Annotated[str, Depends(oauth2_scheme)]):
    """Starts a new adventure."""
    user_id = us.decode_access_token(token)
    # Generate story structure
    prompt= adventure.prompt
    max_levels= adventure.max_levels
    min_words_per_level= adventure.min_words_per_level
    max_words_per_level= adventure.max_words_per_level
    perspective= adventure.perspective.value

    #print(prompt)
    # Generate story
    new_story_json = await generate_new_story(prompt, perspective, min_words_per_level, max_words_per_level)
    new_story=json.loads(new_story_json)
    # Create story structure
    i=0

    # Generate a cover image for the story and upload it to S3:

    new_image = await askDallE_structured(prompt,"1024x1792")    
    image_url = new_image.data[0].url # This is a temporary ChatGPT URL. Expires in 60 minutes.
    s3_image_details = await process_image(image_url)

    options=new_story.get("options")
    adventure = {
        "owner_id": user_id,
        "title": new_story["title"],
        "synopsis": new_story["synopsis"],
        "userPrompt": prompt,
        "createdAt": datetime.utcnow(),
        "perspective": perspective,
        "max_levels": max_levels,
        "min_words_per_level": min_words_per_level,
        "max_words_per_level": max_words_per_level,
        "image_s3_bucket": s3_image_details["bucket_name"],
        "image_s3_key": s3_image_details["s3_key"],
        "nodes": []
    }

    # Save to database
    adventure_collection = get_adventure_collection()
    result = await adventure_collection.insert_one(adventure)

    node= {
        "createdAt": datetime.utcnow(),
        "prev_option_index": None,
        "prev_option_text": None,
        "text": new_story["text"],
        "options": new_story["options"]
    }

    # Append Node to story
    node_result = await update_adventure_nodes(str(result.inserted_id), node)

    return {"adventure_id": str(result.inserted_id)}
    #response = RedirectResponse(url="/", status_code=303)
    #return(response)

@router.put("/continue", response_model=AdventureResponse)
async def continue_adventure(adventure: NodeCreate,  token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure.adventure_id, user_id)
    print(response)
    if response==401:
        raise HTTPException(status_code=401, detail="Content Not authorized for user")
    if response==404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if len(response["nodes"]) < adventure.start_from_node_id+1 or adventure.start_from_node_id<0:
        raise HTTPException(status_code=400, detail=f"Bad Request: Adventure Node {adventure.start_from_node_id} out of range.")
    if len(response["nodes"][adventure.start_from_node_id]["options"]) < adventure.selected_option+1 or adventure.selected_option<0:
        raise HTTPException(status_code=400, detail=f"Bad Request: Option {adventure.selected_option} does not exist.")

    start_from_node_id=adventure.start_from_node_id
    #print("startfrom: "+str(start_from_node_id))
    #print("starting from:"+str(start_from_node_id))

    node = await generate_new_node(adventure.adventure_id, start_from_node_id, adventure.selected_option, adventure.end_after_insert)
    node["prev_option_index"]=adventure.selected_option

    #Generate New Story Node from specified Node.

    result = await update_adventure_nodes(adventure.adventure_id, node)
    new_node_index=start_from_node_id + 1
    return {"adventure_id": adventure.adventure_id, "node_index": new_node_index}
    #response = RedirectResponse(url="/adventure/{adventure_id}/{new_node_index}")
    #return(response)

@router.delete("/delete", response_model=AdventureResponse)
async def adventure_delete(adventure: AdventureDelete, token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure.adventure_id, user_id)
    if response==404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if response==401 or us.decode_access_token(token) != response["owner_id"]:
        raise HTTPException(status_code=401, detail="User not authorized to delete this content.")


    response = await delete_adventure(adventure.adventure_id)
    return {"action": "deleteAdventure", "adventure_id": adventure.adventure_id}

@router.patch("/truncate", response_model=AdventureResponse)
async def adventure_truncate(adventure: AdventureTruncate, token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure.adventure_id, user_id)
    if response==404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if response==401 or us.decode_access_token(token) != response["owner_id"]:
        raise HTTPException(status_code=401, detail="User not authorized to truncate this content.")
    response = await truncate_adventure(adventure.adventure_id, adventure.node_index)
    return {"action": "truncatedAdventure", "adventure_id": adventure.adventure_id,}

@router.get("/getCoverImageURL/{adventure_id}/", response_model=ImageResponse)
async def adventure_cover(adventure_id: str, token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = us.decode_access_token(token)
    response = await get_adventure_for_user(adventure_id, user_id)
    if response==404:
        raise HTTPException(status_code=404, detail="Content Not Found")
    if response==401 or us.decode_access_token(token) != response["owner_id"]:
        raise HTTPException(status_code=401, detail="User not authorized to delete this content.")


    url = await generate_presigned_url(response["image_s3_bucket"], response["image_s3_key"], expiration=3600)
    return {"presigned_url": url}

'''
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
'''

