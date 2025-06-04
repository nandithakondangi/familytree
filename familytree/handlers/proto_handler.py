import logging

from google.protobuf import text_format
from networkx import DiGraph

from familytree.proto import (
    family_tree_pb2,
    utils_pb2,
)

logger = logging.getLogger(__name__)


class ProtoHandler:
    """
    Handler class to perform operations related to protobuf messages.
    """

    def __init__(self):
        """
        Initializes the ProtoHandler with an empty FamilyTree protobuf message.
        """
        self._family_tree = family_tree_pb2.FamilyTree()

    def get_family_tree(self) -> family_tree_pb2.FamilyTree:
        """
        Returns the current FamilyTree protobuf message.

        Returns:
            family_tree_pb2.FamilyTree: The internal FamilyTree message instance.
        """
        return self._family_tree

    def load_from_textproto(self, family_tree_textproto: str) -> None:
        """
        Loads family tree data from a text-formatted protobuf string.

        Args:
            family_tree_textproto: A string containing the family tree data
                                   in text protobuf format.

        Raises:
            text_format.ParseError: If the text proto string is malformed.
            Exception: For other unexpected errors during loading.
        """
        logger.info("Loading FamilyTree from text proto")
        try:
            text_format.Merge(family_tree_textproto, self._family_tree)
            logger.info("Successfully loaded FamilyTree from text proto")
        except text_format.ParseError as e:
            logger.error(f"Error parsing text proto: {e}")
            raise
        except Exception as e:
            logger.exception(
                f"An unexpected error occured when loading FamilyTree from text proto: {e}"
            )

    def update_from_nx_graph(self, nx_graph: DiGraph) -> None:
        """
        Updates the internal FamilyTree protobuf message from a NetworkX DiGraph.

        Note: This method is not yet implemented.

        Args:
            nx_graph: A NetworkX directed graph representing the family tree.
        """
        pass

    def merge_family_trees(
        self, nx_graph: DiGraph, other_family_tree_textproto: str
    ) -> None:
        """
        Merges another family tree (from text proto) into the current one,
        potentially using a NetworkX graph for intermediate representation or updates.

        The process involves:
        1. Updating the current internal state from the provided `nx_graph`.
        2. Loading the `other_family_tree_textproto`.
        3. Deduplicating family members.

        Note: The `update_from_nx_graph` and `_deduplicate_family_members`
              methods are not yet fully implemented.

        Args:
            nx_graph: A NetworkX directed graph, possibly representing the current
                      state or used for merging logic.
            other_family_tree_textproto: A string containing another family tree
                                         data in text protobuf format.
        """
        self.update_from_nx_graph(nx_graph)
        self.load_from_textproto(other_family_tree_textproto)
        self._deduplicate_family_members()  # This method already uses underscore, so it's consistent

    def save_to_textproto(self) -> str:
        """
        Saves the current FamilyTree protobuf message to a text-formatted string.

        Returns:
            str: The family tree data as a text protobuf string.
        """
        return text_format.MessageToString(self._family_tree, indent=2)

    @staticmethod
    def create_family_member(
        id_str: str,
        name: str,
        nicknames: list[str] | None = None,
        date_of_birth: utils_pb2.GregorianDate | None = None,
        traditional_date_of_birth: utils_pb2.TraditionalDate | None = None,
        alive: bool | None = None,
        date_of_death: utils_pb2.GregorianDate | None = None,
        traditional_date_of_death: utils_pb2.TraditionalDate | None = None,
        gender: int
        | None = None,  # Assuming utils_pb2.Gender is an enum, pass its int value
        birth_family_unit_id: int | None = None,
        marriage_family_unit_id: int | None = None,
        wedding_date: utils_pb2.GregorianDate | None = None,
        additional_info: dict[str, str] | None = None,
    ) -> family_tree_pb2.FamilyMember:
        """
        Creates a FamilyMember protobuf message.

        Args:
            id_str: Unique identifier for the family member.
            name: Name of the family member.
            nicknames: List of nicknames.
            date_of_birth: An instance of utils_pb2.GregorianDate.
            traditional_date_of_birth: An instance of utils_pb2.TraditionalDate.
            alive: Boolean indicating if the member is alive. This is an optional field.
                   If None, the field will not be set, preserving its "not present" state.
            date_of_death: An instance of utils_pb2.GregorianDate.
            traditional_date_of_death: An instance of utils_pb2.TraditionalDate.
            gender: Gender of the family member (as an integer enum value from utils_pb2.Gender).
            birth_family_unit_id: ID of the birth family unit. Optional.
            marriage_family_unit_id: ID of the marriage family unit. Optional.
            wedding_date: An instance of utils_pb2.GregorianDate. Optional.
            additional_info: Additional key-value information.

        Returns:
            A family_tree_pb2.FamilyMember message instance.
        """
        member = family_tree_pb2.FamilyMember()

        member.id = id_str
        member.name = name

        if nicknames:
            member.nicknames.extend(nicknames)

        if date_of_birth:
            member.date_of_birth.CopyFrom(date_of_birth)
        if traditional_date_of_birth:
            member.traditional_date_of_birth.CopyFrom(traditional_date_of_birth)

        if alive is not None:  # Only set optional bool if a value is provided
            member.alive = alive

        if date_of_death:
            member.date_of_death.CopyFrom(date_of_death)
        if traditional_date_of_death:
            member.traditional_date_of_death.CopyFrom(traditional_date_of_death)

        if gender is not None:  # Assumes gender is an enum value (int)
            member.gender = gender

        if (
            birth_family_unit_id is not None
        ):  # Only set optional int64 if value is provided
            member.birth_family_unit_id = birth_family_unit_id
        if (
            marriage_family_unit_id is not None
        ):  # Only set optional int64 if value is provided
            member.marriage_family_unit_id = marriage_family_unit_id

        if wedding_date:  # Only set optional message if value is provided
            member.wedding_date.CopyFrom(wedding_date)

        if additional_info:
            for key, value in additional_info.items():
                member.additional_info[key] = value

        return member

    def _deduplicate_family_members(self) -> None:
        """
        Performs deduplication of family members within the FamilyTree.

        This method is intended to resolve conflicts or merge duplicate entries
        after operations like merging family trees.

        Note: This method is not yet implemented.
        """
        pass
