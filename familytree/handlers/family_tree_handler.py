import logging

from familytree.handlers.chat_handler import ChatHandler
from familytree.handlers.graph_handler import GraphHandler
from familytree.handlers.proto_handler import ProtoHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import LoadFamilyRequest, LoadFamilyResponse

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
        return LoadFamilyResponse(
            status=OK_STATUS, message="Family tree loaded successfully."
        )
