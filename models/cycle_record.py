"""
CycleRecord Data Model
"""
from typing import Optional
from models.cycle_time import CycleTime


class CycleRecord:
    """Represents a complete cycle time record"""
    
    def __init__(self, date_str: str, model: str, station: str, 
                 r1: Optional[CycleTime], r2: Optional[CycleTime], r3: Optional[CycleTime],
                 created_by: str, created_at: str, output: str = ""):
        self.date = date_str
        self.model = model
        self.station = station
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.output = output
        self.created_by = created_by
        self.created_at = created_at
        self.modified_by = created_by
        self.modified_at = created_at
    
    @property
    def average(self) -> Optional[CycleTime]:
        """Calculate average cycle time"""
        cycles = [c for c in [self.r1, self.r2, self.r3] if c]
        if not cycles:
            return None
        
        avg_pre = sum(c.pre for c in cycles) / len(cycles)
        avg_machine = sum(c.machine for c in cycles) / len(cycles)
        avg_post = sum(c.post for c in cycles) / len(cycles)
        return CycleTime(avg_pre, avg_machine, avg_post)
    
    def to_dict(self) -> dict:
        """Convert record to dictionary"""
        return {
            "date": self.date,
            "model": self.model,
            "station": self.station,
            "r1": str(self.r1) if self.r1 else "",
            "r2": str(self.r2) if self.r2 else "",
            "r3": str(self.r3) if self.r3 else "",
            "average": str(self.average) if self.average else "",
            "output": self.output,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "modified_by": self.modified_by,
            "modified_at": self.modified_at
        }