from pydantic import BaseModel


class TimeFrameModel(BaseModel):
    start_date: str
    end_date: str

class PotentialDeliveryDateModel(BaseModel):
    potential_date: str

class ConfirmationDeliveryDateModel(BaseModel):
    scheduled_date: str
