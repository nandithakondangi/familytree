import google.protobuf.text_format as text_format
import pytest

import familytree.proto.family_tree_pb2 as family_tree_pb2
import familytree.proto.utils_pb2 as utils_pb2


def create_weasley_family_tree_proto():
    """Creates a FamilyTree protobuf object for the Weasley family."""
    family_tree = family_tree_pb2.FamilyTree()

    # --- Members ---
    arthur = family_tree.members["ARTHW"]
    arthur.id = "ARTHW"
    arthur.name = "Arthur Weasley"
    arthur.gender = utils_pb2.MALE
    arthur.date_of_birth.year = 1950  # Approx
    arthur.date_of_birth.month = 2
    arthur.date_of_birth.date = 6
    arthur.alive = True

    molly = family_tree.members["MOLLW"]
    molly.id = "MOLLW"
    molly.name = "Molly Weasley"
    molly.nicknames.append("Mollywobbles")
    molly.gender = utils_pb2.FEMALE
    molly.date_of_birth.year = 1949  # Approx
    molly.date_of_birth.month = 10
    molly.date_of_birth.date = 30
    molly.alive = True

    bill = family_tree.members["BILLW"]
    bill.id = "BILLW"
    bill.name = "Bill Weasley"
    bill.gender = utils_pb2.MALE
    bill.date_of_birth.year = 1970
    bill.date_of_birth.month = 11
    bill.date_of_birth.date = 29
    bill.alive = True

    charlie = family_tree.members["CHARW"]
    charlie.id = "CHARW"
    charlie.name = "Charlie Weasley"
    charlie.gender = utils_pb2.MALE
    charlie.date_of_birth.year = 1972
    charlie.date_of_birth.month = 12
    charlie.date_of_birth.date = 12
    charlie.alive = True

    percy = family_tree.members["PERCW"]
    percy.id = "PERCW"
    percy.name = "Percy Weasley"
    percy.gender = utils_pb2.MALE
    percy.date_of_birth.year = 1976
    percy.date_of_birth.month = 8
    percy.date_of_birth.date = 22
    percy.alive = True

    fred = family_tree.members["FREDW"]
    fred.id = "FREDW"
    fred.name = "Fred Weasley"
    fred.gender = utils_pb2.MALE
    fred.date_of_birth.year = 1978
    fred.date_of_birth.month = 4
    fred.date_of_birth.date = 1
    fred.alive = False  # Died in Battle of Hogwarts
    fred.date_of_death.year = 1998
    fred.date_of_death.month = 5
    fred.date_of_death.date = 2

    george = family_tree.members["GEORW"]
    george.id = "GEORW"
    george.name = "George Weasley"
    george.gender = utils_pb2.MALE
    george.date_of_birth.year = 1978
    george.date_of_birth.month = 4
    george.date_of_birth.date = 1
    george.alive = True

    ron = family_tree.members["RONAW"]
    ron.id = "RONAW"
    ron.name = "Ron Weasley"
    ron.nicknames.append("Won-Won")
    ron.gender = utils_pb2.MALE
    ron.date_of_birth.year = 1980
    ron.date_of_birth.month = 3
    ron.date_of_birth.date = 1
    ron.alive = True

    ginny = family_tree.members["GINNW"]
    ginny.id = "GINNW"
    ginny.name = "Ginny Weasley"
    ginny.gender = utils_pb2.FEMALE
    ginny.date_of_birth.year = 1981
    ginny.date_of_birth.month = 8
    ginny.date_of_birth.date = 11
    ginny.alive = True
    ginny.traditional_date_of_birth.month = utils_pb2.CHITHIRAI
    ginny.traditional_date_of_birth.star = utils_pb2.ASHWINI

    # --- Relationships ---
    arthur_rel = family_tree.relationships["ARTHW"]
    arthur_rel.spouse_ids.append("MOLLW")
    arthur_rel.children_ids.extend(
        ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    )

    molly_rel = family_tree.relationships["MOLLW"]
    molly_rel.spouse_ids.append("ARTHW")
    molly_rel.children_ids.extend(
        ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    )

    # Add parent relationships for children
    children_ids = ["BILLW", "CHARW", "PERCW", "FREDW", "GEORW", "RONAW", "GINNW"]
    for child_id in children_ids:
        child_rel = family_tree.relationships[child_id]
        # Assuming both Arthur and Molly are parents of all these children
        child_rel.parent_ids.append("ARTHW")
        child_rel.parent_ids.append("MOLLW")

    # Add spouse relationship for Bill (example, not in original fixture)
    # bill_rel = family_tree.relationships["BILLW"]

    return family_tree


@pytest.fixture
def weasley_family_tree_pb():
    """Provides a FamilyTree protobuf object for the Weasley family."""
    return create_weasley_family_tree_proto()


@pytest.fixture
def weasley_family_tree_textproto(weasley_family_tree_pb):
    """Provides the Weasley family tree as a text protobuf string."""
    return text_format.MessageToString(weasley_family_tree_pb, as_utf8=True)
