"""
Security utilities for input sanitization and validation.
"""
import re
import bleach
from typing import Optional


# Allowed HTML tags for story content (very restrictive)
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u']
ALLOWED_ATTRIBUTES = {}

# Maximum lengths to prevent DoS attacks
MAX_PROMPT_LENGTH = 2000
MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 100
MAX_STORY_LENGTH = 50000


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        text: Raw HTML text to sanitize
        
    Returns:
        Sanitized HTML text with only allowed tags
    """
    if not text:
        return ""
    
    return bleach.clean(
        text, 
        tags=ALLOWED_TAGS, 
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def sanitize_prompt(prompt: str) -> str:
    """
    Sanitize user prompts for story generation.
    
    Args:
        prompt: User-provided story prompt
        
    Returns:
        Sanitized prompt text
        
    Raises:
        ValueError: If prompt is too long or contains forbidden content
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    prompt = prompt.strip()
    
    # Check length
    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValueError(f"Prompt too long. Maximum {MAX_PROMPT_LENGTH} characters allowed")
    
    # Remove HTML tags completely for prompts
    prompt = bleach.clean(prompt, tags=[], strip=True)
    
    # Check for suspicious patterns that might be injection attempts
    suspicious_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'on\w+\s*=',  # Event handlers like onclick=
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, prompt, re.IGNORECASE | re.DOTALL):
            raise ValueError("Prompt contains forbidden content")
    
    return prompt


def sanitize_email(email: str) -> str:
    """
    Sanitize and validate email addresses.
    
    Args:
        email: Email address to sanitize
        
    Returns:
        Sanitized email address
        
    Raises:
        ValueError: If email is invalid or too long
    """
    if not email:
        raise ValueError("Email cannot be empty")
    
    email = email.strip().lower()
    
    if len(email) > MAX_EMAIL_LENGTH:
        raise ValueError(f"Email too long. Maximum {MAX_EMAIL_LENGTH} characters allowed")
    
    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email


def sanitize_name(name: str) -> str:
    """
    Sanitize names (API key names, etc.).
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name
        
    Raises:
        ValueError: If name is invalid or too long
    """
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")
    
    name = name.strip()
    
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"Name too long. Maximum {MAX_NAME_LENGTH} characters allowed")
    
    # Remove HTML tags and dangerous characters
    name = bleach.clean(name, tags=[], strip=True)
    
    # Allow only alphanumeric, spaces, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValueError("Name contains invalid characters. Only letters, numbers, spaces, hyphens, and underscores allowed")
    
    return name


def sanitize_story_content(content: str) -> str:
    """
    Sanitize story content while preserving basic formatting.
    
    Args:
        content: Story content to sanitize
        
    Returns:
        Sanitized story content
        
    Raises:
        ValueError: If content is too long
    """
    if not content:
        return ""
    
    if len(content) > MAX_STORY_LENGTH:
        raise ValueError(f"Story content too long. Maximum {MAX_STORY_LENGTH} characters allowed")
    
    # Allow basic formatting tags for stories
    return sanitize_html(content)


def validate_positive_integer(value: int, max_value: Optional[int] = None, field_name: str = "Value") -> int:
    """
    Validate that a value is a positive integer within bounds.
    
    Args:
        value: Integer value to validate
        max_value: Maximum allowed value (optional)
        field_name: Name of the field for error messages
        
    Returns:
        Validated integer value
        
    Raises:
        ValueError: If value is invalid
    """
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    
    if max_value and value > max_value:
        raise ValueError(f"{field_name} cannot exceed {max_value}")
    
    return value


def validate_string_length(value: str, min_length: int = 1, max_length: int = 1000, field_name: str = "Value") -> str:
    """
    Validate string length bounds.
    
    Args:
        value: String to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        field_name: Name of the field for error messages
        
    Returns:
        Validated string
        
    Raises:
        ValueError: If string length is invalid
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")
    
    if len(value) > max_length:
        raise ValueError(f"{field_name} cannot exceed {max_length} characters")
    
    return value
