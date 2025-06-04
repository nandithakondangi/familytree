from pydantic import BaseModel

OK_STATUS: str = "OK"


class FamilyTreeBaseResponse(BaseModel):
    status: str
    message: str
