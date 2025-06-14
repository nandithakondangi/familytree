from typing import Any, Optional

from pydantic import BaseModel, field_serializer, field_validator

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
    new_member_data: dict[str, Any]  # Dictionary representing FamilyMember proto
    source_family_member_id: Optional[str] = None
    relationship_type: Optional[EdgeType] = None

    @field_serializer("relationship_type")
    def serialize_relationship_type(self, v: Optional[EdgeType]):
        if v is None:
            return None
        return v.value  # pragma: no cover

    @field_validator("relationship_type", mode="before")
    @classmethod
    def validate_relationship_type(cls, v: Optional[str]):
        if v is None:
            return None
        # Explicitly map known input strings to EdgeType enum members
        if v == "SPOUSE":
            return EdgeType.SPOUSE
        elif v == "PARENT_TO_CHILD":
            return EdgeType.PARENT_TO_CHILD
        elif v == "CHILD_TO_PARENT":
            return EdgeType.CHILD_TO_PARENT
        else:
            raise ValueError(
                f"Invalid relationship type string for AddFamilyMemberRequest: {v}"
            )


class AddFamilyMemberResponse(FamilyTreeBaseResponse):
    pass
