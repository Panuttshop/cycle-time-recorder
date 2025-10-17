"""
Validation utilities for Cycle Time Recorder
Input validation functions for various data types
"""
import re
from datetime import datetime

def validate_username(username):
    """
    Validate username format
    Rules:
    - 3-20 characters
    - Alphanumeric and underscores only
    - Must start with a letter
    """
    if not username or not isinstance(username, str):
        return False
    
    if len(username) < 3 or len(username) > 20:
        return False
    
    # Must start with letter, contain only alphanumeric and underscore
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, username))

def validate_password(password):
    """
    Validate password strength
    Rules:
    - At least 6 characters
    - Contains at least one letter
    - Contains at least one number
    
    Returns: (is_valid, message)
    """
    if not password or not isinstance(password, str):
        return False, "Password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Check for at least one letter
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_employee_id(employee_id):
    """
    Validate employee ID format
    Can be customized based on your company's format
    """
    if not employee_id or not isinstance(employee_id, str):
        return False, "Employee ID cannot be empty"
    
    # Remove whitespace
    employee_id = employee_id.strip()
    
    if len(employee_id) < 3:
        return False, "Employee ID must be at least 3 characters"
    
    return True, "Valid Employee ID"

def validate_part_number(part_number):
    """
    Validate part number format
    """
    if not part_number or not isinstance(part_number, str):
        return False, "Part number cannot be empty"
    
    # Remove whitespace
    part_number = part_number.strip()
    
    if len(part_number) < 3:
        return False, "Part number must be at least 3 characters"
    
    return True, "Valid Part Number"

def validate_quantity(quantity):
    """
    Validate quantity value
    Must be a positive number
    """
    try:
        qty = float(quantity)
        if qty <= 0:
            return False, "Quantity must be greater than 0"
        return True, "Valid Quantity"
    except (ValueError, TypeError):
        return False, "Quantity must be a valid number"

def validate_cycle_time(cycle_time):
    """
    Validate cycle time value
    Must be a positive number
    """
    try:
        ct = float(cycle_time)
        if ct <= 0:
            return False, "Cycle time must be greater than 0"
        if ct > 86400:  # More than 24 hours in seconds
            return False, "Cycle time seems unreasonably long (max 24 hours)"
        return True, "Valid Cycle Time"
    except (ValueError, TypeError):
        return False, "Cycle time must be a valid number"

def validate_date(date_str):
    """
    Validate date string format
    Expected format: YYYY-MM-DD
    """
    if not date_str:
        return False, "Date cannot be empty"
    
    try:
        datetime.strptime(str(date_str), '%Y-%m-%d')
        return True, "Valid Date"
    except ValueError:
        return False, "Invalid date format. Expected: YYYY-MM-DD"

def validate_time(time_str):
    """
    Validate time string format
    Expected format: HH:MM:SS or HH:MM
    """
    if not time_str:
        return False, "Time cannot be empty"
    
    try:
        # Try HH:MM:SS format
        datetime.strptime(str(time_str), '%H:%M:%S')
        return True, "Valid Time"
    except ValueError:
        try:
            # Try HH:MM format
            datetime.strptime(str(time_str), '%H:%M')
            return True, "Valid Time"
        except ValueError:
            return False, "Invalid time format. Expected: HH:MM or HH:MM:SS"

def validate_email(email):
    """
    Validate email format
    """
    if not email or not isinstance(email, str):
        return False, "Email cannot be empty"
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, "Valid Email"
    
    return False, "Invalid email format"

def validate_machine_id(machine_id):
    """
    Validate machine ID format
    """
    if not machine_id or not isinstance(machine_id, str):
        return False, "Machine ID cannot be empty"
    
    machine_id = machine_id.strip()
    
    if len(machine_id) < 2:
        return False, "Machine ID must be at least 2 characters"
    
    return True, "Valid Machine ID"

def sanitize_input(input_str):
    """
    Sanitize input string to prevent injection attacks
    Removes or escapes potentially dangerous characters
    """
    if not input_str:
        return ""
    
    # Convert to string and strip whitespace
    cleaned = str(input_str).strip()
    
    # Remove or escape special characters that could be used in injection
    # Keep alphanumeric, spaces, and common punctuation
    cleaned = re.sub(r'[<>;"\'\\]', '', cleaned)
    
    return cleaned

def validate_notes(notes, max_length=500):
    """
    Validate notes/comments field
    """
    if not notes:
        return True, "Valid Notes"
    
    if not isinstance(notes, str):
        return False, "Notes must be text"
    
    if len(notes) > max_length:
        return False, f"Notes must be less than {max_length} characters"
    
    return True, "Valid Notes"
