from pydantic import BaseModel, Field
from typing import Dict, List, Literal
import json

class FormulateQuestions(BaseModel):
    document_id: str
    user_id:str
    document_title: str
    document_summary: str
    _ts: float