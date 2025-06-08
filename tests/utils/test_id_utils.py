import re

from familytree.utils.id_utils import generate_family_unit_id, generate_member_id


def test_generate_member_id_pattern():
    """
    Tests that generate_member_id produces an ID matching the expected pattern.
    Pattern: FXXX-MXXX-BXXX-RXXX where X is an uppercase letter or digit.
    """
    member_id = generate_member_id()
    pattern = r"^F[A-Z0-9]{3}-M[A-Z0-9]{3}-B[A-Z0-9]{3}-R[A-Z0-9]{3}$"
    assert re.match(pattern, member_id) is not None, (
        f"Generated member ID '{member_id}' does not match pattern '{pattern}'"
    )


def test_generate_family_unit_id_pattern():
    """
    Tests that generate_family_unit_id produces an ID matching the expected pattern.
    Pattern: FXXX-UXXX-NXXX-TXXX where X is an uppercase letter or digit.
    """
    family_unit_id = generate_family_unit_id()
    pattern = r"^F[A-Z0-9]{3}-U[A-Z0-9]{3}-N[A-Z0-9]{3}-T[A-Z0-9]{3}$"
    assert re.match(pattern, family_unit_id) is not None, (
        f"Generated family unit ID '{family_unit_id}' does not match pattern '{pattern}'"
    )
