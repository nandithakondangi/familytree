from pydantic import BaseModel

from familytree.models.base_model import FamilyTreeBaseResponse


class CreateFamilyResponse(FamilyTreeBaseResponse):
    pass


class LoadFamilyRequest(BaseModel):
    filename: str
    content: str


class LoadFamilyResponse(FamilyTreeBaseResponse):
    pass
