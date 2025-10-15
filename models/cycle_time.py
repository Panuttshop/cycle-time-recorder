"""
CycleTime Data Model
"""
import re
from typing import Optional


class CycleTime:
    """Represents a single cycle time reading"""
    
    def __init__(self, pre: float, machine: float, post: float):
        self.pre = pre
        self.machine = machine
        self.post = post
    
    @classmethod
    def parse(cls, s: str) -> Optional['CycleTime']:
        """
        Parse cycle time from string format: 5(12)4
        
        Args:
            s: String in format pre(machine)post
            
        Returns:
            CycleTime object or None if invalid
        """
        if not s or not isinstance(s, str):
            return None
        
        pattern = r"^\s*(\d+(?:\.\d+)?)\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*(\d+(?:\.\d+)?)\s*$"
        m = re.match(pattern, s.strip())
        if not m:
            return None
        
        return cls(float(m.group(1)), float(m.group(2)), float(m.group(3)))
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.pre:.1f}({self.machine:.1f}){self.post:.1f}"
    
    @property
    def total(self) -> float:
        """Total cycle time"""
        return self.pre + self.machine + self.post