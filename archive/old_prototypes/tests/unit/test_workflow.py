from src.app.domain.workflow import (
    can_transition,
)


def test_draft_to_submitted():

    assert can_transition(
        "Draft",
        "Submitted",
    )


def test_draft_to_posted():

    assert not can_transition(
        "Draft",
        "Posted",
    )
    