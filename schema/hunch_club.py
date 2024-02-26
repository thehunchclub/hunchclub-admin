from pydantic import BaseModel
import datetime as dt
from typing import List, Optional

class TipSchema(BaseModel):
    id: str = ""
    datetime: dt.datetime = dt.datetime.utcnow()
    participants: list = []
    event_name: str = ""
    event_type: str = ""
    market_type: Optional[str] = None
    selection: str = ""
    odds: float = 1.0
    description: str = ""
    language: str = "en-US"
    event_result: str = ""
    bet_result: str = ""
    odds_url: str = ""
    publish_free: bool = False
    publish_vip: bool = False