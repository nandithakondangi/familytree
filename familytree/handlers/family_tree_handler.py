import logging

from google.protobuf.json_format import ParseDict

from familytree.handlers.chat_handler import ChatHandler
from familytree.handlers.graph_handler import EdgeType, GraphHandler
from familytree.handlers.proto_handler import ProtoHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import (
    AddFamilyMemberRequest,
    AddFamilyMemberResponse,
    LoadFamilyRequest,
    LoadFamilyResponse,
)
from familytree.proto import family_tree_pb2

logger = logging.getLogger(__name__)


class FamilyTreeHandler:
    """
    Handler class to manage family tree operations.
    """

    def __init__(self):
        """
        Initializes the FamilyTreeHandler.

        This sets up instances of GraphHandler, ProtoHandler, and ChatHandler
        to manage different aspects of family tree data and interactions.
        """
        self.graph_handler = GraphHandler()
        self.proto_handler = ProtoHandler()
        self.chat_handler = ChatHandler()

    def load_family_tree(
        self, load_family_request: LoadFamilyRequest
    ) -> LoadFamilyResponse:
        """
        Loads a family tree from a text protobuf representation.

        Args:
            load_family_request: A LoadFamilyRequest object containing the
                                 family tree data as a text protobuf string.

        Returns:
            A LoadFamilyResponse object indicating the status of the operation.
        """
        self.proto_handler.load_from_textproto(load_family_request.content)
        self.graph_handler.create_from_proto(self.proto_handler.get_family_tree())
        response = LoadFamilyResponse(
            status=OK_STATUS,  # pyrefly: ignore
            message="Family tree loaded successfully.",  # pyrefly: ignore
        )
        return response

    def add_family_member(
        self, add_family_member_request: AddFamilyMemberRequest
    ) -> AddFamilyMemberResponse:
        new_member_to_add_dict = add_family_member_request.new_member_data
        new_member_to_add = ParseDict(
            new_member_to_add_dict, family_tree_pb2.FamilyMember()
        )

        self.graph_handler.add_member(new_member_to_add.id, new_member_to_add)

        if (
            add_family_member_request.source_family_member_id is not None
            and add_family_member_request.relationship_type is not None
        ):
            # Add the primary relationship and its reverse
            primary_relationship: dict[str, str | EdgeType] = {
                "source_id": add_family_member_request.source_family_member_id,
                "target_id": new_member_to_add.id,
                "relationship_type": add_family_member_request.relationship_type,
            }
            relations_to_add: list[dict[str, str | EdgeType]] = [primary_relationship]
            relations_to_add.append(
                self._add_reverse_relationship(primary_relationship)
            )

            if add_family_member_request.infer_relationships:
                relations_to_add.extend(self.infer_relationships(primary_relationship))

            for relationship in relations_to_add:
                # The relationship_type in this loop is guaranteed to be an EdgeType instance
                if relationship["relationship_type"] == EdgeType.PARENT_TO_CHILD:
                    self.graph_handler.add_child_relation(
                        str(relationship["source_id"]), str(relationship["target_id"])
                    )
                elif relationship["relationship_type"] == EdgeType.CHILD_TO_PARENT:
                    self.graph_handler.add_parent_relation(
                        str(relationship["source_id"]), str(relationship["target_id"])
                    )
                elif relationship["relationship_type"] == EdgeType.SPOUSE:
                    self.graph_handler.add_spouse_relation(
                        str(relationship["source_id"]), str(relationship["target_id"])
                    )
                else:
                    logger.error(
                        f"Invalid or unexpected relationship type: {relationship['relationship_type']}"
                    )

        response = AddFamilyMemberResponse(
            status=OK_STATUS,  # pyrefly: ignore
            message=f"{new_member_to_add.name} added successfully to the family.",
        )
        return response

    def infer_relationships(
        self, main_relationship: dict[str, str | EdgeType]
    ) -> list[dict[str, str | EdgeType]]:
        inferred_relationships: list[dict[str, str | EdgeType]] = []

        if main_relationship["relationship_type"] == EdgeType.PARENT_TO_CHILD:
            inferred_relationships.extend(
                self._infer_child_for_spouse(main_relationship)
            )
        elif main_relationship["relationship_type"] == EdgeType.CHILD_TO_PARENT:
            inferred_relationships.extend(
                self._infer_spouse_for_parent(main_relationship)
            )
        elif main_relationship["relationship_type"] == EdgeType.SPOUSE:
            inferred_relationships.extend(
                self._infer_parent_for_child(main_relationship)
            )

        return inferred_relationships

    def render_family_tree(self) -> str:
        return self.graph_handler.render_graph_to_html()

    def _add_reverse_relationship(
        self, relationship: dict[str, str | EdgeType]
    ) -> dict[str, str | EdgeType]:
        return {
            "source_id": relationship["target_id"],
            "target_id": relationship["source_id"],
            "relationship_type": EdgeType.CHILD_TO_PARENT
            if relationship["relationship_type"] == EdgeType.PARENT_TO_CHILD
            else EdgeType.PARENT_TO_CHILD
            if relationship["relationship_type"] == EdgeType.CHILD_TO_PARENT
            else EdgeType.SPOUSE,
        }

    def _infer_child_for_spouse(
        self, primary_relationship: dict[str, str | EdgeType]
    ) -> list[dict[str, str | EdgeType]]:
        source_parent = str(primary_relationship["source_id"])
        if self.graph_handler.has_spouse(source_parent):
            spouse_id = self.graph_handler.get_spouse(source_parent)
            assert spouse_id is not None
            inferred_relationships = [
                {
                    "source_id": spouse_id,
                    "target_id": str(primary_relationship["target_id"]),
                    "relationship_type": EdgeType.PARENT_TO_CHILD,
                }
            ]
            inferred_relationships.append(
                self._add_reverse_relationship(inferred_relationships[0])
            )
            return inferred_relationships
        return []

    def _infer_spouse_for_parent(
        self, primary_relationship: dict[str, str | EdgeType]
    ) -> list[dict[str, str | EdgeType]]:
        source_child = str(primary_relationship["source_id"])
        if self.graph_handler.has_parent(source_child):
            parent_id = self.graph_handler.get_parent(source_child)
            assert parent_id is not None
            inferred_relationships = [
                {
                    "source_id": parent_id,
                    "target_id": str(primary_relationship["target_id"]),
                    "relationship_type": EdgeType.SPOUSE,
                }
            ]
            inferred_relationships.append(
                self._add_reverse_relationship(inferred_relationships[0])
            )
            return inferred_relationships
        return []

    def _infer_parent_for_child(
        self, primary_relationship: dict[str, str | EdgeType]
    ) -> list[dict[str, str | EdgeType]]:
        source_spouse = str(primary_relationship["source_id"])
        if self.graph_handler.has_child(source_spouse):
            children = self.graph_handler.get_children(source_spouse)
            inferred_relationships = []
            for child in children:
                parent = {
                    "source_id": child,
                    "target_id": str(primary_relationship["target_id"]),
                    "relationship_type": EdgeType.CHILD_TO_PARENT,
                }
                inferred_relationships.extend(
                    [parent, self._add_reverse_relationship(parent)]
                )
            return inferred_relationships
        return []
