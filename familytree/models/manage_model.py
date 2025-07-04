from builtins import isinstance
from typing import Any, Optional

from pydantic import BaseModel, field_serializer, field_validator

from familytree.handlers.graph_handler import EdgeType
from familytree.models.base_model import FamilyTreeBaseResponse


class RelationshipTypeValidatorMixin:
    """Mixin for validating and serializing EdgeType fields."""

    @field_serializer("relationship_type")
    def serialize_relationship_type(self, v: Optional[EdgeType]):
        if v is None:
            return None
        return v.name  # pragma: no cover

    @field_validator("relationship_type", mode="before")  # pyrefly: ignore
    @classmethod
    def validate_relationship_type(cls, v: Optional[str | EdgeType]):
        if v is None:
            return None
        if isinstance(v, EdgeType):
            return v
        # Explicitly map known input strings to EdgeType enum members
        if v == "SPOUSE":
            return EdgeType.SPOUSE
        elif v == "PARENT_TO_CHILD":
            return EdgeType.PARENT_TO_CHILD
        elif v == "CHILD_TO_PARENT":
            return EdgeType.CHILD_TO_PARENT
        else:
            raise ValueError(
                f"Invalid relationship type string for {cls.__name__}: {v}"
            )


class CreateFamilyResponse(FamilyTreeBaseResponse):
    pass


class LoadFamilyRequest(BaseModel):
    filename: str
    content: str


class LoadFamilyResponse(FamilyTreeBaseResponse):
    pass


class AddFamilyMemberRequest(RelationshipTypeValidatorMixin, BaseModel):
    infer_relationships: bool
    new_member_data: dict[str, Any]  # Dictionary representing FamilyMember proto
    source_family_member_id: Optional[str] = None
    relationship_type: Optional[EdgeType] = None


class AddFamilyMemberResponse(FamilyTreeBaseResponse):
    new_member_id: Optional[str] = None


class AddRelationshipRequest(RelationshipTypeValidatorMixin, BaseModel):
    source_member_id: str
    target_member_id: str
    relationship_type: EdgeType
    add_inverse_relationship: bool = True


class AddRelationshipResponse(FamilyTreeBaseResponse):
    pass


class UpdateFamilyMemberRequest(BaseModel):
    member_id: str
    updated_member_data: dict[str, Any]


class UpdateFamilyMemberResponse(FamilyTreeBaseResponse):
    pass


class DeleteFamilyMemberRequest(BaseModel):
    member_id: str
    remove_orphaned_neighbors: bool = False


class DeleteFamilyMemberResponse(FamilyTreeBaseResponse):
    pass


class DeleteRelationshipRequest(BaseModel):
    source_member_id: str
    target_member_id: str
    remove_inverse_relationship: bool = True


class DeleteRelationshipResponse(FamilyTreeBaseResponse):
    pass


class SaveFamilyResponse(FamilyTreeBaseResponse):
    family_tree_txtpb: str


class ExportInteractiveGraphResponse(FamilyTreeBaseResponse):
    graph_html: Optional[str] = None
