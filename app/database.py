from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from typing import Optional
from bson import ObjectId
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# Helper to access User collections
async def get_user_collection() -> Collection:
    return db["users"]


async def get_user_by_id(user_id) -> Collection:
    try:
        user_collection = await get_user_collection()
        user = await user_collection.find_one({"_id":ObjectId(user_id)}, {"email": 1, "hashed_password": 0})
        if not user:
            return None
        else:
            return user
    except Exception as e:
        return None

async def get_user_by_email(email) -> Collection:
    try:
        user_collection = await get_user_collection()
        user = await user_collection.find_one({"email":email})
        if not user:
            return None
        else:
            return user
    except Exception as e:
        return None


async def create_user(email, hashed_password, createdAt):
    try:
        user_collection= await get_user_collection()
        user={
        "email": email,
        "hashed_password":hashed_password,
        "createdAt": createdAt
        }
        result = await user_collection.insert_one(user)
        object_id = result.inserted_id
        return object_id
    except Exception as e:
        return None




# Helper to access Adventure collections
def get_adventure_collection() -> Collection:
    return db["adventures"]

async def get_all_adventures(owner_id):
    collection=db["adventures"]
    cursor = collection.find({"$or": [{"owner_id": owner_id}, {"is_public": True}]})  # Asynchronous cursor
    adventures = await cursor.to_list(length=None)  # Await the cursor and convert it to a list
    return adventures

# Function to get a single adventure document by its ID
async def get_adventure_by_id(adventure_id: str) -> Optional[dict]:
    """
    Retrieve an adventure document by its ID.
    
    Args:
        adventure_id (str): The ID of the adventure to retrieve.

    Returns:
        dict: The adventure document if found, otherwise None.
    """
    try:
        adventure_collection = get_adventure_collection()
        # Ensure adventure_id is a valid ObjectId
        if not ObjectId.is_valid(adventure_id):
            return None
        adventure = await adventure_collection.find_one({"_id": ObjectId(adventure_id)})
        return adventure
    except Exception as e:
        return None

async def create_adventure(adventure: dict):
    result = await adventure_collection.insert_one(adventure)
    return result

async def update_adventure_nodes(adventure_id: str, data: dict):
    try:
        if not ObjectId.is_valid(adventure_id):
            raise ValueError("Invalid ObjectId")

        result = await db["adventures"].update_one(
            {"_id": ObjectId(adventure_id)},  # Match document by _id
            {"$push": {"nodes": data}}  # Push the dictionary to the array
        )
        return result.raw_result
    except Exception as e:
        return None

# Helper to access Node Collections
def get_node_collection() -> Collection:
    return db["nodes"]

async def get_node_by_id(node_id: str) -> Optional[dict]:
    """
    Retrieve an adventure document by its ID.
    
    Args:
        adventure_id (str): The ID of the adventure to retrieve.

    Returns:
        dict: The adventure document if found, otherwise None.
    """
    try:
        node_collection = get_node_collection()
        # Ensure adventure_id is a valid ObjectId
        if not ObjectId.is_valid(node_id):
            return None
        node = await node_collection.find_one({"_id": ObjectId(node_id)})
        return node
    except Exception as e:
        return None

async def get_node_by_level(adventure_id: str, level: int) -> Optional[dict]:
    """
    Retrieve an adventure document by its ID.
    
    Args:
        adventure_id (str): The ID of the adventure to retrieve.

    Returns:
        dict: The adventure document if found, otherwise None.
    """
    try:
        node_collection = get_node_collection()
        # Ensure adventure_id is a valid ObjectId
        if not ObjectId.is_valid(adventure_id):
            return None
        node = await node_collection.find_one({"_id": ObjectId(adventure_id), "level": level})
        return node
    except Exception as e:
        return None

async def delete_adventure(adventure_id: str):
    try:
        if not ObjectId.is_valid(adventure_id):
            raise ValueError("Invalid ObjectId")

        result = await db["adventures"].delete_one(
            {"_id": ObjectId(adventure_id)},  # Match document by _id
        )
        return result.raw_result
    except Exception as e:
        return None


async def truncate_adventure(adventure_id: str, node_index: int):
    try:
        if not ObjectId.is_valid(adventure_id):
            raise ValueError("Invalid ObjectId")
        if node_index<0:
            raise ValueError("Invalid node_index. Must be greater than zero.")
        doc = await get_adventure_by_id(adventure_id)
        if doc and "nodes" in doc:
            truncated_nodes = doc["nodes"][:node_index]
            result = await db["adventures"].update_one(
                {"_id": ObjectId(adventure_id)},
                {"$set": {"nodes": truncated_nodes}}
            )
            return result.raw_result
    except Exception as e:
        return None

