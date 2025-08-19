import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from bson import ObjectId

from app.database import get_api_key_collection


async def generate_api_key(
    name: str, scopes: List[str], expires_in_days: Optional[int] = None
):
    """
    Generate a new API key with secure random token.

    :param name: Human-readable name for the key
    :param scopes: List of permissions/scopes
    :param expires_in_days: Optional expiration in days
    :return: Dictionary with key data including the actual API key
    """
    # Generate secure random key
    api_key = f"ak_{secrets.token_urlsafe(32)}"

    # Hash for storage (never store the actual key)
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Set expiration
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    # Create key document
    key_data = {
        "name": name,
        "key_hash": key_hash,
        "scopes": scopes,
        "expires_at": expires_at,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "last_used": None,
    }

    # Store in database
    collection = get_api_key_collection()
    result = await collection.insert_one(key_data)

    # Return the actual key (only shown once) along with metadata
    return {"key_id": str(result.inserted_id), "api_key": api_key, **key_data}


async def verify_api_key(api_key: str):
    """
    Verify API key and return scopes.

    :param api_key: The API key to verify
    :return: Dictionary with key data including scopes
    :raises: Exception if key is invalid
    """
    if not api_key.startswith("ak_"):
        raise Exception("Invalid API key format")

    # Hash the provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Look up in database
    collection = get_api_key_collection()
    key_data = await collection.find_one({"key_hash": key_hash})

    if not key_data:
        raise Exception("Invalid API key")

    if not key_data.get("is_active", False):
        raise Exception("API key is inactive")

    # Check expiration
    if key_data.get("expires_at") and key_data["expires_at"] < datetime.utcnow():
        raise Exception("API key expired")

    # Update last used timestamp
    await collection.update_one(
        {"_id": key_data["_id"]}, {"$set": {"last_used": datetime.utcnow()}}
    )

    return {
        "key_id": str(key_data["_id"]),
        "name": key_data["name"],
        "scopes": key_data["scopes"],
        "created_at": key_data["created_at"],
        "expires_at": key_data.get("expires_at"),
    }


async def get_api_key_by_id(key_id: str):
    """
    Get API key information by ID (without the actual key).

    :param key_id: The API key ID
    :return: Key information dictionary
    """
    collection = get_api_key_collection()
    key_data = await collection.find_one({"_id": ObjectId(key_id)})

    if not key_data:
        return None

    # Don't return the key_hash for security
    return {
        "key_id": str(key_data["_id"]),
        "name": key_data["name"],
        "scopes": key_data["scopes"],
        "created_at": key_data["created_at"],
        "expires_at": key_data.get("expires_at"),
        "is_active": key_data.get("is_active", False),
        "last_used": key_data.get("last_used"),
    }


async def list_api_keys():
    """
    List all API keys (without actual keys).

    :return: List of key information dictionaries
    """
    collection = get_api_key_collection()
    cursor = collection.find({}, {"key_hash": 0})  # Exclude the hash

    keys = []
    async for key in cursor:
        keys.append(
            {
                "key_id": str(key["_id"]),
                "name": key["name"],
                "scopes": key["scopes"],
                "created_at": key["created_at"],
                "expires_at": key.get("expires_at"),
                "is_active": key.get("is_active", False),
                "last_used": key.get("last_used"),
            }
        )

    return keys


async def update_api_key(key_id: str, updates: dict):
    """
    Update API key information.

    :param key_id: The API key ID
    :param updates: Dictionary of fields to update
    :return: True if successful
    """
    collection = get_api_key_collection()

    # Remove any fields that shouldn't be updated
    safe_updates = {
        k: v for k, v in updates.items() if k in ["name", "scopes", "is_active"]
    }

    if not safe_updates:
        return False

    result = await collection.update_one(
        {"_id": ObjectId(key_id)}, {"$set": safe_updates}
    )

    return result.modified_count > 0


async def deactivate_api_key(key_id: str):
    """
    Deactivate an API key.

    :param key_id: The API key ID
    :return: True if successful
    """
    return await update_api_key(key_id, {"is_active": False})


async def delete_api_key(key_id: str):
    """
    Permanently delete an API key.

    :param key_id: The API key ID
    :return: True if successful
    """
    collection = get_api_key_collection()
    result = await collection.delete_one({"_id": ObjectId(key_id)})
    return result.deleted_count > 0
