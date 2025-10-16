import hashlib
import secrets

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with a salt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password with salt
    """
    # Generate a random salt
    salt = secrets.token_hex(16)
    
    # Combine password and salt, then hash
    password_salt = f"{password}{salt}"
    hashed = hashlib.sha256(password_salt.encode()).hexdigest()
    
    # Return salt and hash combined
    return f"{salt}:{hashed}"

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password
    
    Args:
        password: Plain text password to verify
        hashed_password: Hashed password with salt (format: salt:hash)
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Split salt and hash
        salt, original_hash = hashed_password.split(':')
        
        # Hash the provided password with the same salt
        password_salt = f"{password}{salt}"
        new_hash = hashlib.sha256(password_salt.encode()).hexdigest()
        
        # Compare hashes
        return new_hash == original_hash
    except (ValueError, AttributeError):
        # Handle malformed hashed_password
        return False

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for at least one number or special character (optional but recommended)
    has_number = any(char.isdigit() for char in password)
    has_letter = any(char.isalpha() for char in password)
    
    if not has_letter:
        return False, "Password must contain at least one letter"
    
    return True, "Password is valid"

def generate_random_password(length: int = 12) -> str:
    """
    Generate a random secure password
    
    Args:
        length: Length of password (default: 12)
        
    Returns:
        Random password string
    """
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return password
