"""
Security and Password Management
"""
import hashlib
import secrets
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Password requirements (defined here to avoid circular import)
PASSWORD_MIN_LENGTH = 8


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hash password using PBKDF2
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
        
    Returns:
        Hashed password with salt
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                    salt.encode('utf-8'), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password
        hashed: Hashed password with salt
        
    Returns:
        True if password matches
    """
    try:
        if '$' not in hashed:
            return False
        
        salt, pwd_hash = hashed.split('$', 1)
        return hash_password(password, salt) == hashed
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"รหัสผ่านต้องยาวอย่างน้อย {PASSWORD_MIN_LENGTH} ตัวอักษร"
    if not any(c.isupper() for c in password):
        return False, "รหัสผ่านต้องมีอักษรตัวใหญ่"
    if not any(c.isdigit() for c in password):
        return False, "รหัสผ่านต้องมีตัวเลข"
    return True, ""