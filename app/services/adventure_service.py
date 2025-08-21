import json
import os
import re

from bson.objectid import ObjectId
from dotenv import load_dotenv

from app.database import (get_adventure_by_id, get_adventure_collection,
                          get_all_adventures, get_node_by_id,
                          get_node_by_level)
from app.schemas.adventure import Outcomes
from app.services.chatgpt_service import (askOpenAI_structured,
                                          assistantMessage, developerMessage,
                                          userMessage)
# from app.services.auth_service import hash_password, verify_password
from app.services.user_service import decode_access_token

load_dotenv()


def regexp_extract(string, pattern):
    match = re.search(pattern, string)
    if match:
        return match.group(1)


def clean_option(text):
    return re.sub(r"\s*###OPTION###\s*", "", text).strip()


def null_to_empty_string(value):
    return "" if value is None else value


async def get_adventure_for_user(adventure_id, user_id):
    """Checks if user_id has permission to view adventure_id. If so, returns the adventure dict"""
    adventure = await get_adventure_by_id(adventure_id)
    if not adventure:
        return 404
    
    # Check if user is admin
    from app.services.user_service import is_user_admin
    is_admin = await is_user_admin(user_id)
    
    # Admin users can access any adventure
    if is_admin:
        return adventure
    
    # Regular users can only access their own adventures or public ones
    if (not adventure.get("is_public")) and adventure.get("owner_id") != user_id:
        return 401
    
    return adventure


async def get_full_story(adventure_id):
    """Returns the full adventure as a string"""
    adventure = await get_adventure_by_id(adventure_id)
    adventure_nodes = adventure.get("nodes")
    full_story_text = ""
    for this_node in adventure_nodes:
        full_story_text = full_story_text + this_node["text"]
    return full_story_text


async def clone_adventure(adventure_id: str, user_id: str):
    """Creates a clone of an existing adventure."""
    # Get the original adventure
    original_adventure = await get_adventure_for_user(adventure_id, user_id)
    
    if original_adventure == 404:
        raise Exception("Adventure not found")
    if original_adventure == 401:
        raise Exception("User not authorized to access this adventure")
    
    # Create a new adventure object with cloned data
    from datetime import datetime
    from app.database import create_adventure, update_adventure_nodes
    
    cloned_adventure = {
        "owner_id": user_id,
        "title": f"(copy) {original_adventure['title']}",
        "synopsis": original_adventure['synopsis'],
        "userPrompt": original_adventure.get('userPrompt', ''),
        "createdAt": datetime.utcnow(),
        "perspective": original_adventure.get('perspective', 'Second Person'),
        "max_levels": original_adventure.get('max_levels', 10),
        "min_words_per_level": original_adventure.get('min_words_per_level', 100),
        "max_words_per_level": original_adventure.get('max_words_per_level', 200),
        "nodes": [],
        "clone_of": adventure_id,  # Reference to the original adventure
    }
    
    # Copy image fields if they exist
    if 'image_s3_bucket' in original_adventure and 'image_s3_key' in original_adventure:
        cloned_adventure['image_s3_bucket'] = original_adventure['image_s3_bucket']
        cloned_adventure['image_s3_key'] = original_adventure['image_s3_key']
    
    # Save the cloned adventure to database
    result = await create_adventure(cloned_adventure)
    
    # Clone all nodes from the original adventure
    if 'nodes' in original_adventure and original_adventure['nodes']:
        for node in original_adventure['nodes']:
            cloned_node = {
                "createdAt": datetime.utcnow(),
                "prev_option_index": node.get('prev_option_index'),
                "prev_option_text": node.get('prev_option_text'),
                "text": node.get('text', ''),
                "options": node.get('options', []),
            }
            await update_adventure_nodes(str(result.inserted_id), cloned_node)
    
    return {
        "adventure_id": str(result.inserted_id),
        "title": cloned_adventure['title'],
        "synopsis": cloned_adventure['synopsis'],
        "createdAt": cloned_adventure['createdAt'],
        "clone_of": adventure_id,
    }


async def generate_new_story(prompt, perspective, min_words, max_words):
    """Generates a story node using ChatGPT."""

    option_instructions = developerMessage(
        f"""
    Create an english language choose-your-own adventure style novel based on the info provided by the user.
    You will return these pieces of information:
    - Title of Story (maximum 5 words)
    - Synopsis of Story (maximum 200 words)
    - Text of the first chapter of the story, between {min_words} and {max_words}  in length.
    - an array of 2-3 choices for the user to take after reading the text of the first chapter.
    """
    )
    userPrompt = userMessage(prompt)

    context = [option_instructions]
    new_story = await askOpenAI_structured(context, userPrompt, "new")
    return new_story


# Continue a story at a selected level using the chosen option.
async def generate_new_node(adventure_id, node_id, selected_option, end_after_insert):
    adventure = await get_adventure_by_id(adventure_id)
    """Generates a story node using ChatGPT."""
    adventure_title = adventure.get("title")
    perspective = adventure.get("perspective")
    synopsis = adventure.get("synopsis")
    min_words_per_level = adventure.get("min_words_per_level")
    max_words_per_level = adventure.get("max_words_per_level")

    max_words_per_level = adventure.get("max_words_per_level")
    previous_text = await get_full_story(adventure_id)
    language = adventure.get("language")
    title = adventure.get("title")

    selected_option_text = adventure["nodes"][node_id]["options"][selected_option]

    if end_after_insert == Outcomes.FINISH:
        continuation_text = "Text for the final chapter of the story, with a positive ending for the protagonist."
        options_array_instructions = f"""an empty array in the options field"""
    elif end_after_insert == Outcomes.DEAD:
        continuation_text = (
            "Text for the final chapter of the story, in which the protagonist dies."
        )
        options_array_instructions = f"""an array in the options field"""
    else:
        continuation_text = f"""Text of the next chapter of the story"""
        options_array_instructions = f"""an array of 2-3 choices for the user to take after reading the text of the first chapter."""

    context = []

    context.append(
        developerMessage(
            f"""
    You are creating a choose-your-own-adventure story based on the user's instructions.
    The title of the story is: {adventure_title}
    The perspective of the story is: { perspective }
    The synopsis of the story is:
    { synopsis }
    """
        )
    )

    for node in adventure["nodes"]:
        context.append(assistantMessage(node["text"]))

    context.append(
        developerMessage(
            f"""
    return these pieces of information:
    - {continuation_text} - between {min_words_per_level} and {min_words_per_level}  in length.
    - {options_array_instructions}"""
        )
    )

    prompt = userMessage(selected_option_text)
    new_node_json = await askOpenAI_structured(context, prompt, "node")
    new_node = json.loads(new_node_json)
    new_node["prev_option_text"] = selected_option_text
    return new_node


async def fetch_adventures(owner_id):
    if owner_id:
        adventures = await get_all_adventures(owner_id)
        # print(adventures)
        output = []
        for adventure in adventures:
            output.append(
                {
                    "id": str(adventure["_id"]),
                    "perspective": adventure["perspective"],
                    "createdAt": adventure["createdAt"],
                    "title": adventure["title"],
                    "synopsis": adventure["synopsis"],
                    "max_levels": adventure["max_levels"],
                    "min_words_per_level": adventure["min_words_per_level"],
                    "max_words_per_level": adventure["max_words_per_level"],
                    "numNodes": len(adventure["nodes"]),
                }
            )
        return output
    else:
        raise ValueError("Invalid token")
