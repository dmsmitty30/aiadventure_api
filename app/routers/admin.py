from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

import app.services.user_service as us
from app.schemas.api_key import (APIKeyCreate, APIKeyList, APIKeyResponse,
                                 APIKeyUpdate)
from app.schemas.user import UserCreate
from app.services.api_key_service import (deactivate_api_key, delete_api_key,
                                          generate_api_key, get_api_key_by_id,
                                          list_api_keys, update_api_key)
from app.services.user_service import register_user
from app.services.auth_service import require_any_auth
from app.security import sanitize_name, sanitize_email, validate_string_length, validate_positive_integer

router = APIRouter()


def extract_user_id(auth_result: dict) -> str:
    """Extract user ID from auth_result, handling both user and API key authentication."""
    if auth_result["type"] == "user":
        return auth_result["id"]
    else:
        return auth_result["info"]["key_id"]


async def verify_admin_token(auth_result: Annotated[dict, Depends(require_any_auth)]):
    """Verify that the user has admin privileges."""
    user_id = extract_user_id(auth_result)

    # Check if user has admin role
    is_admin = await us.is_user_admin(user_id)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    return user_id


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate, admin_id: Annotated[str, Depends(verify_admin_token)]
):
    """Create a new API key (admin only)"""
    try:
        # Sanitize and validate inputs
        name = sanitize_name(key_data.name)
        scopes = [sanitize_name(scope) for scope in key_data.scopes] if key_data.scopes else []
        expires_in_days = None
        
        if key_data.expires_in_days is not None:
            expires_in_days = validate_positive_integer(
                key_data.expires_in_days, 
                max_value=365, 
                field_name="Expires in days"
            )
        
        api_key = await generate_api_key(
            name=name,
            scopes=scopes,
            expires_in_days=expires_in_days,
        )
        return api_key
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/api-keys", response_model=APIKeyList)
async def list_all_api_keys(admin_id: Annotated[str, Depends(verify_admin_token)]):
    """List all API keys (admin only)"""
    try:
        keys = await list_api_keys()
        return {"api_keys": keys}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list API keys: {str(e)}"
        )


@router.get("/api-keys/{key_id}")
async def get_api_key_info(
    key_id: str, admin_id: Annotated[str, Depends(verify_admin_token)]
):
    """Get information about a specific API key (admin only)"""
    try:
        key_info = await get_api_key_by_id(key_id)
        if not key_info:
            raise HTTPException(status_code=404, detail="API key not found")
        return key_info
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get API key info: {str(e)}"
        )


@router.put("/api-keys/{key_id}")
async def update_api_key_info(
    key_id: str,
    updates: APIKeyUpdate,
    admin_id: Annotated[str, Depends(verify_admin_token)],
):
    """Update API key information (admin only)"""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in updates.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid updates provided")

        success = await update_api_key(key_id, update_data)
        if not success:
            raise HTTPException(
                status_code=404, detail="API key not found or no changes made"
            )

        return {"message": "API key updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update API key: {str(e)}"
        )


@router.patch("/api-keys/{key_id}/deactivate")
async def deactivate_api_key_endpoint(
    key_id: str, admin_id: Annotated[str, Depends(verify_admin_token)]
):
    """Deactivate an API key (admin only)"""
    try:
        success = await deactivate_api_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")

        return {"message": "API key deactivated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to deactivate API key: {str(e)}"
        )


@router.delete("/api-keys/{key_id}")
async def delete_api_key_endpoint(
    key_id: str, admin_id: Annotated[str, Depends(verify_admin_token)]
):
    """Permanently delete an API key (admin only)"""
    try:
        success = await delete_api_key(key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API key not found")

        return {"message": "API key deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete API key: {str(e)}"
        )


@router.post("/users", response_model=dict)
async def create_user_admin(
    user_data: UserCreate, admin_id: Annotated[str, Depends(verify_admin_token)]
):
    """Create a new user (admin only)"""
    try:
        new_user_id = await register_user(
            user_data.email, user_data.password, user_data.role.value
        )
        return {
            "message": "User created successfully",
            "user_id": str(new_user_id),
            "email": user_data.email,
            "role": user_data.role.value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user_admin(
    user_id: str, admin_id: Annotated[str, Depends(verify_admin_token)]
):
    """Delete a user (admin only)"""
    try:
        # Prevent admin from deleting themselves
        if user_id == admin_id:
            raise HTTPException(
                status_code=400, detail="Admin cannot delete themselves"
            )
        
        # Check if user exists
        user = await us.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete the user
        success = await us.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete user")
        
        return {
            "message": "User deleted successfully",
            "deleted_user_id": user_id,
            "deleted_user_email": user.get("email", "Unknown")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete user: {str(e)}"
        )


@router.get("/debug/user-role")
async def debug_user_role(auth_result: Annotated[dict, Depends(require_any_auth)]):
    """Debug endpoint to check user role (temporary)"""
    user_id = extract_user_id(auth_result)

    # Get user details with more debugging
    user = await us.get_user_by_id(user_id)
    user_role = await us.get_user_role(user_id)
    is_admin = await us.is_user_admin(user_id)

    # Additional debugging info
    from bson import ObjectId

    is_valid_object_id = ObjectId.is_valid(user_id)

    # Direct database debugging
    from app.database import get_user_collection

    collection = await get_user_collection()

    # Try to find the user directly
    try:
        direct_user = await collection.find_one({"_id": ObjectId(user_id)})
        direct_user_without_id = None
        if direct_user:
            # Convert ObjectId to string for JSON serialization
            direct_user_without_id = {}
            for k, v in direct_user.items():
                if k == "_id":
                    direct_user_without_id[k] = str(v)
                elif k != "hashed_password":
                    direct_user_without_id[k] = v
    except Exception as e:
        direct_user = None
        direct_user_without_id = f"Error: {str(e)}"

    return {
        "user_id": user_id,
        "is_valid_object_id": is_valid_object_id,
        "user_data": user,
        "role": user_role,
        "is_admin": is_admin,
        "direct_db_lookup": direct_user_without_id,
        "message": "This endpoint shows your current user role for debugging",
    }
