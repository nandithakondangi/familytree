import logging

import networkx as nx

logger = logging.getLogger(__name__)


class GraphHandler:
    """
    Handler class to perform graph operations.
    """

    def __init__(self, graph: nx.DiGraph | None = None):
        """
        Initializes the GraphHandler.

        Args:
            graph: An optional NetworkX DiGraph. If None, an empty DiGraph
                   is created.
        """
        if graph is None:
            self.graph = nx.DiGraph()
        else:
            self.graph = graph
