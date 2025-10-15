"""
Input Validation Functions
"""
from typing import Tuple
from models.cycle_time import CycleTime


def validate_cycle_input(s: str) -> Tuple[bool, str]:
    """
    Validate cycle time format
    
    Args:
        s: Input string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not s or not s.strip():
        return True, ""
    
    if CycleTime.parse(s) is None:
        return False, "รูปแบบไม่ถูกต้อง (ตัวอย่าง: 5(12)4)"
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    username = username.strip()
    if not username:
        return False, "username ว่าง"
    if len(username) < 3:
        return False, "username ต้องยาวอย่างน้อย 3 ตัวอักษร"
    return True, ""