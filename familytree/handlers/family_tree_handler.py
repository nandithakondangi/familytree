import logging

from google.protobuf.json_format import ParseDict

from familytree.exceptions import InvalidInputError, MemberNotFoundError
from familytree.handlers.chat_handler import ChatHandler
from familytree.handlers.graph_handler import EdgeType, GraphHandler
from familytree.handlers.proto_handler import ProtoHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.graph_model import MemberInfoResponse
from familytree.models.manage_model import (
    AddFamilyMemberRequest,
    AddFamilyMemberResponse,
    AddRelationshipRequest,
    AddRelationshipResponse,
    DeleteFamilyMemberRequest,
    DeleteFamilyMemberResponse,
    DeleteRelationshipRequest,
    DeleteRelationshipResponse,
    LoadFamilyRequest,
    LoadFamilyResponse,
    SaveFamilyResponse,
    UpdateFamilyMemberRequest,
    UpdateFamilyMemberResponse,
)
from familytree.proto import family_tree_pb2
from familytree.utils import id_utils

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

    def add_family_member(
        self, add_family_member_request: AddFamilyMemberRequest
    ) -> AddFamilyMemberResponse:
        """
        Adds a new family member to the graph.

        If a source member and relationship are provided, it also establishes the
        relationship and infers additional relationships if requested.

        Args:
            add_family_member_request: The request object containing data for the
                                       new member and any initial relationship.

        Returns:
            An AddFamilyMemberResponse object with the status and ID of the new member.
        """
        new_member_to_add_dict = add_family_member_request.new_member_data
        new_member_to_add = ParseDict(
            new_member_to_add_dict, family_tree_pb2.FamilyMember()
        )
        new_member_to_add.id = id_utils.generate_member_id()
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
                relations_to_add.extend(self._infer_relationships(primary_relationship))

            for relationship in relations_to_add:
                self._add_relationship_to_graph(relationship)

        return AddFamilyMemberResponse(
            status=OK_STATUS,  # pyrefly: ignore
            new_member_id=new_member_to_add.id,
            message=f"{new_member_to_add.name} added successfully to the family.",  # pyrefly: ignore
        )

    def add_relationship(
        self, request: AddRelationshipRequest
    ) -> AddRelationshipResponse:
        """
        Adds a relationship between two existing family members.

        Optionally adds the inverse relationship as well.

        Args:
            request: The request object containing the source member, target member,
                     and relationship type.

        Returns:
            An AddRelationshipResponse object indicating the status of the operation.
        """
        primary_relationsip = {
            "source_id": request.source_member_id,
            "target_id": request.target_member_id,
            "relationship_type": request.relationship_type,
        }
        self._add_relationship_to_graph(primary_relationsip)
        if request.add_inverse_relationship:
            self._add_relationship_to_graph(
                self._add_reverse_relationship(primary_relationsip)
            )
        return AddRelationshipResponse(
            status=OK_STATUS,
            message=f"Relationship between {request.source_member_id} and {request.target_member_id} added successfully.",
        )

    def update_family_member(
        self, request: UpdateFamilyMemberRequest
    ) -> UpdateFamilyMemberResponse:
        """
        Updates the information of an existing family member.

        Args:
            request: The request object containing the member ID and the updated data.

        Returns:
            An UpdateFamilyMemberResponse object indicating the status of the operation.

        Raises:
            MemberNotFoundError: If no member with the given ID is found.
        """
        try:
            updated_family_member = ParseDict(
                request.updated_member_data, family_tree_pb2.FamilyMember()
            )
            self.graph_handler.update_family_member(
                request.member_id, updated_family_member
            )
            return UpdateFamilyMemberResponse(
                status=OK_STATUS,
                message=f"Member {request.member_id} updated successfully.",
            )
        except KeyError as e:
            logger.error(
                f"Member with ID '{request.member_id}' not found for update.",
                exc_info=True,
            )
            raise MemberNotFoundError(
                member_id=request.member_id, operation="update_family_member"
            ) from e

    def get_member_info(self, user_id: str) -> MemberInfoResponse:
        """
        Retrieves the information for a specific family member.

        Args:
            user_id: The ID of the member to retrieve information for.

        Returns:
            A MemberInfoResponse object containing the member's data.

        Raises:
            MemberNotFoundError: If no member with the given user_id is found.
        """
        try:
            member_info = self.graph_handler.get_member_info(user_id)
            return MemberInfoResponse(
                status=OK_STATUS,  # pyrefly: ignore
                message="Member info retrieved successfully.",  # pyrefly: ignore
                member_info=member_info,
            )
        except KeyError as e:
            logger.error(f"Member with ID '{user_id}' not found.", exc_info=True)
            raise MemberNotFoundError(
                member_id=user_id, operation="get_member_info"
            ) from e

    def delete_family_member(
        self, request: DeleteFamilyMemberRequest
    ) -> DeleteFamilyMemberResponse:
        """
        Deletes a family member from the graph.

        Optionally removes neighbors who become orphaned after the deletion.

        Args:
            request: The request object containing the ID of the member to delete.

        Returns:
            A DeleteFamilyMemberResponse object indicating the status of the operation.
        """
        self.graph_handler.remove_member(
            request.member_id, request.remove_orphaned_neighbors
        )
        return DeleteFamilyMemberResponse(
            status=OK_STATUS, message="Member deleted successfully."
        )

    def delete_relationship(
        self, request: DeleteRelationshipRequest
    ) -> DeleteRelationshipResponse:
        """
        Deletes a relationship between two family members.

        Optionally removes the inverse relationship as well.

        Args:
            request: The request object containing the source and target member IDs.

        Returns:
            A DeleteRelationshipResponse object indicating the status of the operation.
        """
        self.graph_handler.remove_relationship(
            request.source_member_id,
            request.target_member_id,
            request.remove_inverse_relationship,
        )
        return DeleteRelationshipResponse(
            status=OK_STATUS, message="Relationship deleted successfully."
        )

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

    def render_family_tree(self, theme: str) -> str:
        """
        Renders the current family tree graph to an HTML string.

        Args:
            theme: The color theme to use for rendering (e.g., 'light', 'dark').

        Returns:
            The HTML content of the rendered graph as a string.
        """
        return self.graph_handler.render_graph_to_html(theme)

    def save_family_tree(self, visible_only: bool) -> SaveFamilyResponse:
        """
        Saves the current state of the family tree graph to a text protobuf.

        Args:
            visible_only: (Currently unused) A flag to indicate if only the
                          visible portion of the graph should be saved.

        Returns:
            A SaveFamilyResponse object containing the family tree as a text
            protobuf string.
        """
        self.proto_handler.update_from_nx_graph(
            self.graph_handler.get_family_graph(),
            self.graph_handler.get_family_unit_graph(),
        )
        return SaveFamilyResponse(
            status=OK_STATUS,
            message="Created family tree text proto",
            family_tree_txtpb=self.proto_handler.save_to_textproto(),  # pyrefly: ignore
        )

    def ask_about_family(self, query: str) -> str:
        return self.chat_handler.send_query_to_agent_team(query)

    def _add_relationship_to_graph(self, relationship: dict[str, str | EdgeType]):
        """
        Adds a single relationship to the graph based on its type.

        This is a helper method that calls the appropriate graph handler method.

        Args:
            relationship: A dictionary containing source_id, target_id, and
                          relationship_type.

        Raises:
            InvalidInputError: If the relationship_type is not recognized.
        """
        if relationship["relationship_type"] == EdgeType.PARENT_TO_CHILD:
            self.graph_handler.add_child_relation(
                str(relationship["source_id"]),
                str(relationship["target_id"]),
            )
        elif relationship["relationship_type"] == EdgeType.CHILD_TO_PARENT:
            self.graph_handler.add_parent_relation(
                str(relationship["source_id"]),
                str(relationship["target_id"]),
            )
        elif relationship["relationship_type"] == EdgeType.SPOUSE:
            self.graph_handler.add_spouse_relation(
                str(relationship["source_id"]),
                str(relationship["target_id"]),
            )
        else:
            error_message = f"Invalid or unexpected relationship type: {relationship['relationship_type']}"
            logger.error(error_message)
            raise InvalidInputError(
                operation="Adding relationship",
                field="relationship_type",
                description=error_message,
            )

    def _infer_relationships(
        self, main_relationship: dict[str, str | EdgeType]
    ) -> list[dict[str, str | EdgeType]]:
        """
        Infers additional relationships based on a primary relationship.

        For example, if a parent-child link is added, this can infer that the
        parent's spouse is also a parent to the child.

        Args:
            main_relationship: The primary relationship from which to infer others.

        Returns:
            A list of inferred relationship dictionaries.
        """
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

    def _add_reverse_relationship(
        self, relationship: dict[str, str | EdgeType]
    ) -> dict[str, str | EdgeType]:
        """
        Creates the reverse of a given relationship.

        - PARENT_TO_CHILD becomes CHILD_TO_PARENT.
        - CHILD_TO_PARENT becomes PARENT_TO_CHILD.
        - SPOUSE remains SPOUSE.

        Args:
            relationship: The original relationship dictionary.

        Returns:
            A new dictionary representing the reverse relationship.
        """
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
        """
        Infers that a new child is also the child of the source's spouse.

        If a PARENT_TO_CHILD relationship is added, and the parent has a spouse,
        this method creates a PARENT_TO_CHILD relationship from the spouse to
        the new child.

        Args:
            primary_relationship: The PARENT_TO_CHILD relationship.

        Returns:
            A list containing the new inferred relationship and its reverse,
            or an empty list if no spouse is found.
        """
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
        """
        Infers that a new parent is the spouse of an existing parent.

        If a CHILD_TO_PARENT relationship is added, and the child already has
        another parent, this method creates a SPOUSE relationship between the
        two parents.

        Args:
            primary_relationship: The CHILD_TO_PARENT relationship.

        Returns:
            A list containing the new inferred relationship and its reverse,
            or an empty list if no other parent is found.
        """
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
        """
        Infers that a new spouse is a parent to existing children.

        If a SPOUSE relationship is added, and one of the spouses already has
        children, this method creates CHILD_TO_PARENT relationships from those
        children to the new spouse.

        Args:
            primary_relationship: The SPOUSE relationship.

        Returns:
            A list of new inferred parent-child relationships and their reverses,
            or an empty list if there are no children.
        """
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
