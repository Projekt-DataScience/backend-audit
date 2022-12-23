from pydantic import BaseModel


class SingleGroupAnalytics(BaseModel):
    group_name: str = ""
    percent_green: float = 0.0
    percent_yellow: float = 0.0
    percent_red: float = 0.0
