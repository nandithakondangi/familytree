import logging

from google.protobuf import text_format
from networkx import DiGraph
from thefuzz import fuzz

from familytree.proto import family_tree_pb2
from familytree.utils import id_utils
from familytree.utils.graph_types import EdgeType

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
        text_format.Merge(family_tree_textproto, self._family_tree)
        logger.info("Successfully loaded FamilyTree from text proto")

    def update_from_nx_graph(
        self, nx_graph: DiGraph, family_unit_map: dict[str, family_tree_pb2.FamilyUnit]
    ) -> None:
        """
        Updates the internal FamilyTree protobuf message from a NetworkX DiGraph.

        Note: This method is not yet implemented.

        Args:
           nx_graph: A NetworkX directed graph representing the family tree.
        """
        nodes_from_graph = nx_graph.nodes(data=True)
        edges_from_graph = nx_graph.edges(data=True)

        self._update_missing_family_members(nodes_from_graph)
        self._update_missing_relationships(edges_from_graph)
        self._update_family_units(family_unit_map)

    def merge_family_trees(
        self,
        nx_graph: DiGraph,
        family_unit_map: dict[str, family_tree_pb2.FamilyUnit],
        other_family_tree_textproto: str,
    ) -> None:
        """
        Merges another family tree (from text proto) into the current one,
        potentially using a NetworkX graph for intermediate representation or updates.

        The process involves:
        1. Updating the current internal state from the provided `nx_graph`.
        2. Loading the `other_family_tree_textproto` into a temporary FamilyTree object.
        3. Deduplicating family members between the current and the other tree.
        4. Updating the internal state with the merged tree.

        Args:
            nx_graph: A NetworkX directed graph, possibly representing the current
                      state or used for merging logic.
            other_family_tree_textproto: A string containing another family tree
                                         data in text protobuf format.
        """
        self.update_from_nx_graph(nx_graph, family_unit_map)

        other_family_tree = family_tree_pb2.FamilyTree()
        text_format.Merge(other_family_tree_textproto, other_family_tree)

        merged_tree = self._deduplicate_family_members(
            self._family_tree, other_family_tree
        )
        self._family_tree = merged_tree

    def save_to_textproto(self) -> str:
        """
        Saves the current FamilyTree protobuf message to a text-formatted string.

        Returns:
            str: The family tree data as a text protobuf string.
        """
        return text_format.MessageToString(self._family_tree, indent=2)

    def _update_missing_family_members(self, nodes_from_graph):
        """
        Updates or adds family members in the internal FamilyTree message from a list of graph nodes.

        Args:
            nodes_from_graph: A list of nodes from a NetworkX graph, where each node
                              has data containing a 'data' object with an 'attributes'
                              field, which is a FamilyMember message.
        """
        for node_id, node_data in nodes_from_graph:
            if node_id not in self._family_tree.members:
                self._family_tree.members[node_id].CopyFrom(
                    node_data["data"].attributes
                )
            else:
                self._family_tree.members[node_id].MergeFrom(
                    node_data["data"].attributes
                )

    def _update_missing_relationships(self, edges_from_graph):
        """
        Updates or adds relationships in the internal FamilyTree message from a list of graph edges.

        Args:
            edges_from_graph: A list of edges from a NetworkX graph, where each edge
                              has data containing a 'data' object with an 'edge_type'
                              field.
        """
        for source_id, target_id, edge_data in edges_from_graph:
            if (
                edge_data["data"].edge_type == EdgeType.PARENT_TO_CHILD
                and target_id
                not in self._family_tree.relationships[source_id].children_ids
            ):
                self._family_tree.relationships[source_id].children_ids.append(
                    target_id
                )
            elif (
                edge_data["data"].edge_type == EdgeType.CHILD_TO_PARENT
                and target_id
                not in self._family_tree.relationships[source_id].parent_ids
            ):
                self._family_tree.relationships[source_id].parent_ids.append(target_id)
            elif (
                edge_data["data"].edge_type == EdgeType.SPOUSE
                and target_id
                not in self._family_tree.relationships[source_id].spouse_ids
            ):
                self._family_tree.relationships[source_id].spouse_ids.append(target_id)

    def _update_family_units(self, family_units_map):
        """
        Updates or adds family units in the internal FamilyTree message from a dictionary.

        Args:
            family_units_map: A dictionary where keys are family unit IDs and values
                              are FamilyUnit protobuf messages.
        """
        for family_unit_id, family_unit in family_units_map.items():
            if family_unit_id not in self._family_tree.family_units:
                self._family_tree.family_units[family_unit_id].CopyFrom(family_unit)
            else:
                self._family_tree.family_units[family_unit_id].MergeFrom(family_unit)

    def _calculate_similarity(self, member1, member2):
        """
        Calculates a normalized similarity score between two family members based on
        their names, nicknames, gender, and date of birth.

        The name similarity is a weighted average of the best matches between the names
        and nicknames of the two members.

        Args:
            member1: The first FamilyMember protobuf message.
            member2: The second FamilyMember protobuf message.

        Returns:
            A float between 0 and 1 representing the similarity score.
        """
        total_score = 0
        max_score = 0

        # Name similarity (including nicknames)
        names1 = [member1.name] + list(member1.nicknames)
        names2 = [member2.name] + list(member2.nicknames)

        if len(names1) < len(names2):
            shorter_list, longer_list = names1, names2
        else:
            shorter_list, longer_list = names2, names1

        if not shorter_list:
            name_score = 0
        else:
            best_match_scores = []
            for name_short in shorter_list:
                best_score = 0
                for name_long in longer_list:
                    score = fuzz.token_sort_ratio(name_short, name_long)
                    if score > best_score:
                        best_score = score
                best_match_scores.append(best_score)

            name_score = sum(best_match_scores) / len(best_match_scores)

        total_score += name_score
        max_score += 100

        # Gender similarity
        if member1.gender and member2.gender:
            if member1.gender == member2.gender:
                total_score += 20
            max_score += 20

        # Date of birth similarity
        if member1.HasField("date_of_birth") and member2.HasField("date_of_birth"):
            if member1.date_of_birth.year == member2.date_of_birth.year:
                total_score += 20
            max_score += 20

        print(total_score, max_score)

        return total_score / max_score if max_score > 0 else 0

    def _get_neighbor_similarity(self, member1_id, member2_id, tree1, tree2, id_map):
        """
        Calculates a similarity score between two family members based on the similarity
        of their immediate family members (parents, children, and spouses).

        Args:
            member1_id: The ID of the first member.
            member2_id: The ID of the second member.
            tree1: The FamilyTree object containing the first member.
            tree2: The FamilyTree object containing the second member.
            id_map: A dictionary mapping IDs from the second tree to the first tree.

        Returns:
            A float between 0 and 1 representing the neighbor similarity score.
        """
        score = 0
        comparisons = 0

        # Compare parents
        parents1_ids = tree1.relationships.get(
            member1_id, family_tree_pb2.Relationships()
        ).parent_ids
        parents2_ids = tree2.relationships.get(
            member2_id, family_tree_pb2.Relationships()
        ).parent_ids
        if parents1_ids and parents2_ids:
            for p1_id in parents1_ids:
                for p2_id in parents2_ids:
                    p1 = tree1.members.get(p1_id)
                    p2 = tree2.members.get(p2_id)
                    if p1 and p2:
                        score += fuzz.token_sort_ratio(p1.name, p2.name)
                        comparisons += 1

        # Compare children
        children1_ids = tree1.relationships.get(
            member1_id, family_tree_pb2.Relationships()
        ).children_ids
        children2_ids = tree2.relationships.get(
            member2_id, family_tree_pb2.Relationships()
        ).children_ids
        if children1_ids and children2_ids:
            for c1_id in children1_ids:
                for c2_id in children2_ids:
                    c1 = tree1.members.get(c1_id)
                    c2 = tree2.members.get(c2_id)
                    if c1 and c2:
                        score += fuzz.token_sort_ratio(c1.name, c2.name)
                        comparisons += 1

        # Compare spouses
        spouses1_ids = tree1.relationships.get(
            member1_id, family_tree_pb2.Relationships()
        ).spouse_ids
        spouses2_ids = tree2.relationships.get(
            member2_id, family_tree_pb2.Relationships()
        ).spouse_ids
        if spouses1_ids and spouses2_ids:
            for s1_id in spouses1_ids:
                for s2_id in spouses2_ids:
                    s1 = tree1.members.get(s1_id)
                    s2 = tree2.members.get(s2_id)
                    if s1 and s2:
                        score += fuzz.token_sort_ratio(s1.name, s2.name)
                        comparisons += 1

        return score / (comparisons * 100) if comparisons > 0 else 0

    def _deduplicate_family_members(
        self,
        family_tree_1: family_tree_pb2.FamilyTree,
        family_tree_2: family_tree_pb2.FamilyTree,
    ) -> family_tree_pb2.FamilyTree:
        """
        Identifies and merges duplicate family members between two FamilyTree objects.

        This method iterates through each member of the second family tree and tries to
        find a matching member in the first tree. The matching is based on a
        similarity score that considers names, nicknames, gender, date of birth, and
        the similarity of immediate family members.

        If a match is found above a certain threshold, the information from the second
        member is merged into the first. Otherwise, the member from the second tree is
        added as a new member to the merged tree.

        Args:
            family_tree_1: The first FamilyTree object.
            family_tree_2: The second FamilyTree object.

        Returns:
            A new FamilyTree object with duplicate members merged.
        """
        merged_tree = family_tree_pb2.FamilyTree()
        merged_tree.CopyFrom(family_tree_1)
        id_map = {m_id: m_id for m_id in family_tree_1.members}

        MATCH_THRESHOLD = 0.8

        for member2_id, member2 in family_tree_2.members.items():
            best_match_id = None
            highest_final_score = 0

            for member1_id, member1 in merged_tree.members.items():
                if member1_id not in family_tree_1.members:
                    continue

                base_similarity = self._calculate_similarity(member1, member2)
                neighbor_similarity = self._get_neighbor_similarity(
                    member1_id, member2_id, merged_tree, family_tree_2, id_map
                )

                final_score = base_similarity + (0.2 * neighbor_similarity)

                if final_score > highest_final_score:
                    highest_final_score = final_score
                    best_match_id = member1_id
            print(highest_final_score)

            if highest_final_score > MATCH_THRESHOLD:
                matched_id = str(best_match_id)
                id_map[member2_id] = matched_id
                merged_tree.members[matched_id].MergeFrom(member2)
            else:
                new_id = id_utils.generate_member_id()
                id_map[member2_id] = new_id
                merged_tree.members[new_id].CopyFrom(member2)
                merged_tree.members[new_id].id = new_id

        # Update relationships and family units from family_tree_2
        for original_id, rels2 in family_tree_2.relationships.items():
            new_id = id_map.get(original_id)
            if not new_id:
                continue

            for child_id in rels2.children_ids:
                merged_tree.relationships[new_id].children_ids.append(
                    id_map.get(child_id, child_id)
                )
            for spouse_id in rels2.spouse_ids:
                merged_tree.relationships[new_id].spouse_ids.append(
                    id_map.get(spouse_id, spouse_id)
                )
            for parent_id in rels2.parent_ids:
                merged_tree.relationships[new_id].parent_ids.append(
                    id_map.get(parent_id, parent_id)
                )

        for original_id, unit2 in family_tree_2.family_units.items():
            new_id = id_map.get(original_id)
            if not new_id:
                continue
            if new_id not in merged_tree.family_units:
                merged_tree.family_units[new_id].CopyFrom(unit2)

        return merged_tree
