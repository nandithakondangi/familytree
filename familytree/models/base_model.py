from pydantic import BaseModel

OK_STATUS: str = "OK"
ERROR_STATUS: str = "ERROR"


class FamilyTreeBaseResponse(BaseModel):
    status: str
    message: str
