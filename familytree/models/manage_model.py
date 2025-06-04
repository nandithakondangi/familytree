from typing import Any

from pydantic import BaseModel, field_serializer

from familytree.handlers.graph_handler import EdgeType
from familytree.models.base_model import FamilyTreeBaseResponse


class CreateFamilyResponse(FamilyTreeBaseResponse):
    pass


class LoadFamilyRequest(BaseModel):
    filename: str
    content: str


class LoadFamilyResponse(FamilyTreeBaseResponse):
    pass


class AddFamilyMemberRequest(BaseModel):
    infer_relationships: bool
    new_member_data: dict[str, Any]
    source_family_member_id: str
    relationship_type: EdgeType

    @field_serializer("relationship_type")
    def serialize_relationship_type(self, v: EdgeType):
        return v.value


class AddFamilyMemberResponse(FamilyTreeBaseResponse):
    pass
