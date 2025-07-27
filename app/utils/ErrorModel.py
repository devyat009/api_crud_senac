from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any

class ErrorDetail(BaseModel):
    """Schema for specific error details"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None
    
    
def create_error_response(message: str, field: str = None, code: str = None) -> dict:
    """Error response format"""
    return {
        "success": False,
        "message": message,
        "field": field,
        "code": code,
        "timestamp": datetime.now().isoformat()
    }
