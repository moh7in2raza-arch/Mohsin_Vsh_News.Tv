TRANSITIONS = {

    "Draft": {"Submitted"},

    "Submitted": {
        "Approved",
        "Draft",
    },

    "Approved": {
        "Posted",
        "Draft",
    },

    "Posted": {
        "Reversed",
    },

    "Reversed": set(),

    "Deleted": set(),
}


def can_transition(
    old_status: str,
    new_status: str,
) -> bool:

    return (
        new_status
        in TRANSITIONS.get(
            old_status,
            set(),
        )
    )
    