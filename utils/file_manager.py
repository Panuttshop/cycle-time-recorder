"""
File Management and Data Persistence
"""
import json
import os
import logging
from typing import Dict, List
from datetime import datetime
from config.settings import DATA_DIR, USERS_FILE, DATA_FILE, AUDIT_FILE, DEFAULT_ADMIN
from models.cycle_record import CycleRecord
from models.cycle_time import CycleTime
from utils.security import hash_password

logger = logging.getLogger(__name__)


def ensure_files():
    """Create necessary files and directories if they don't exist"""
    # Create data directory
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Create users file
    if not os.path.exists(USERS_FILE):
        users_data = {
            DEFAULT_ADMIN[0]: {
                "password_hash": hash_password(DEFAULT_ADMIN[1]),
                "role": "Admin"
            },
            "alice": {
                "password_hash": hash_password("Alice123"),
                "role": "Member"
            }
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    # Create data file
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    # Create audit file
    if not os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)


def load_users() -> Dict:
    """Load users from JSON file"""
    ensure_files()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}


def save_users(users: Dict) -> bool:
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving users: {e}")
        return False


def load_records() -> List[CycleRecord]:
    """Load records from JSON file"""
    ensure_files()
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            records = []
            for item in data:
                rec = CycleRecord(
                    item['date'], item['model'], item['station'],
                    CycleTime.parse(item.get('r1', '')),
                    CycleTime.parse(item.get('r2', '')),
                    CycleTime.parse(item.get('r3', '')),
                    item['created_by'], item['created_at'],
                    item.get('output', '')  # Load output field
                )
                rec.modified_by = item.get('modified_by', item['created_by'])
                rec.modified_at = item.get('modified_at', item['created_at'])
                records.append(rec)
            return records
    except Exception as e:
        logger.error(f"Error loading records: {e}")
        return []


def save_records(records: List[CycleRecord]) -> bool:
    """Save records to JSON file"""
    try:
        data = [r.to_dict() for r in records]
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving records: {e}")
        return False


def add_audit_log(action: str, username: str, details: str = ""):
    """
    Log an action for audit trail
    
    Args:
        action: Action type
        username: User who performed action
        details: Additional details
    """
    try:
        with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "username": username,
        "details": details
    })
    
    try:
        with open(AUDIT_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving audit log: {e}")