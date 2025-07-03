import random
import string

BLOCK_LENGTH = 4
CHARS = string.ascii_uppercase + string.digits


def _generate_random_block(base: str) -> str:
    return base + "".join(random.choices(CHARS, k=BLOCK_LENGTH - 1))


def generate_member_id() -> str:
    member_id_base = "FMBR"
    return "-".join([_generate_random_block(c) for c in member_id_base])


def generate_family_unit_id() -> str:
    family_unit_base = "FUNT"
    return "-".join([_generate_random_block(c) for c in family_unit_base])


def generate_family_conversation_id() -> str:
    family_conversation_base = "FCON"
    return "-".join([_generate_random_block(c) for c in family_conversation_base])
