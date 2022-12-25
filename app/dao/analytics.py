from pydantic import BaseModel


class SingleGroupAnalytics(BaseModel):
    group_name: str = ""
    percent_green: float = 0.0
    percent_yellow: float = 0.0
    percent_red: float = 0.0


class AuditAnalytics(BaseModel):
    month: int = 0
    year: int = 0
    
    num_green: int = 0
    num_yellow: int = 0
    num_red: int = 0

    percent_green: float = 0.0
    percent_yellow: float = 0.0
    percent_red: float = 0.0
