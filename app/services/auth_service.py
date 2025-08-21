import logging
from typing import Optional, Union

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.api_key_service import verify_api_key
from app.services.user_service import decode_access_token

# Set up logging
logger = logging.getLogger(__name__)

# HTTP Bearer scheme for authentication
api_key_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    auto_error=True,
    description="Enter your JWT token (without 'Bearer' prefix)"
)


async def get_current_user_or_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(api_key_scheme),
) -> Union[str, dict]:
    """
    Authenticate user via JWT token or API key.
    Returns either user_id (for JWT) or key_info (for API key).
    """
    try:
        print("=" * 50)
        print("🔍 AUTH DEBUG START")
        print("=" * 50)
        print(f"DEBUG: credentials received: {credentials}")
        print(f"DEBUG: credentials type: {type(credentials)}")
        print(f"DEBUG: credentials.credentials: {credentials.credentials}")
        print(f"DEBUG: credentials.scheme: {credentials.scheme}")
        print("=" * 50)
        
        # Also log to FastAPI's logging system
        logger.info("🔍 AUTH DEBUG START")
        logger.info(f"DEBUG: credentials received: {credentials}")
        logger.info(f"DEBUG: credentials type: {type(credentials)}")
        logger.info(f"DEBUG: credentials.credentials: {credentials.credentials}")
        logger.info(f"DEBUG: credentials.scheme: {credentials.scheme}")
        
        token = credentials.credentials

        # Try JWT token first
        print(f"DEBUG: Checking if token starts with 'eyJ': {token.startswith('eyJ')}")
        if token.startswith("eyJ"):  # JWT tokens typically start with "eyJ"
            print("DEBUG: Token appears to be JWT, attempting to decode...")
            try:
                user_id = decode_access_token(token)
                print(f"DEBUG: Successfully decoded JWT, user_id: {user_id}")
                return {"type": "user", "id": user_id}
            except Exception as e:
                print(f"DEBUG: Failed to decode JWT: {str(e)}")
                pass

        # Try API key
        if token.startswith("ak_"):
            try:
                key_info = await verify_api_key(token)
                return {"type": "api_key", "info": key_info}
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Invalid API key: {str(e)}")

        # If neither works
        raise HTTPException(
            status_code=401, detail="Invalid authentication token or API key"
        )
        
    except Exception as e:
        print(f"ERROR in get_current_user_or_api_key: {str(e)}")
        logger.error(f"ERROR in get_current_user_or_api_key: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Authentication error: {str(e)}"
        )


async def require_user_auth(
    auth_result: Union[str, dict] = Depends(get_current_user_or_api_key)
) -> str:
    """
    Require user authentication (JWT token only).
    API keys are not allowed for user-specific operations.
    """
    if isinstance(auth_result, dict) and auth_result["type"] == "user":
        return auth_result["id"]

    raise HTTPException(
        status_code=403,
        detail="User authentication required. API keys are not allowed for this operation.",
    )


async def require_api_key_auth(
    auth_result: Union[str, dict] = Depends(get_current_user_or_api_key)
) -> dict:
    """
    Require API key authentication.
    JWT tokens are not allowed for API key operations.
    """
    if isinstance(auth_result, dict) and auth_result["type"] == "api_key":
        return auth_result["info"]

    raise HTTPException(
        status_code=403,
        detail="API key authentication required. JWT tokens are not allowed for this operation.",
    )


async def require_any_auth(
    auth_result: Union[str, dict] = Depends(get_current_user_or_api_key)
) -> Union[str, dict]:
    """
    Accept either user authentication or API key authentication.
    Returns the appropriate authentication result.
    """
    return auth_result


def check_scope(required_scopes: list[str]):
    """
    Decorator to check if the authenticated entity has required scopes.
    Use with API key authentication.
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would need to be implemented based on how you want to pass auth info
            # For now, this is a placeholder for the scope checking logic
            pass

        return wrapper

    return decorator
