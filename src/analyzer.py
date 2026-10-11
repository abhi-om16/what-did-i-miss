import pytest

from src.analyzer import analyze_messages, build_summary


@pytest.fixture
def sample_messages():
    return [
        {
            "sender": "Aisha",
            "text": "The project demo is Friday at 3 PM.",
        },
        {
            "sender": "Rahul",
            "text": "I'll finish the slides by Thursday.",
        },
        {
            "sender": "Meera",
            "text": "We still need someone to test the app.",
        },
        {
            "sender": "Aisha",
            "text": "Abhi, can you test the app by Thursday evening and report any bugs?",
        },
        {
            "sender": "Rahul",
            "text": "Decision: we'll use the new dashboard design for the demo.",
        },
        {
            "sender": "Meera",
            "text": "I'll send the test checklist tomorrow.",
        },
    ]


def test_analyzer_returns_expected_structure(sample_messages):
    result = analyze_messages(sample_messages)

    assert isinstance(result, dict)
    assert result["message_count"] == len(sample_messages)
    assert isinstance(result["tasks"], list)
    assert isinstance(result["decisions"], list)
    assert isinstance(result["key_points"], list)


def test_analyzer_detects_tasks(sample_messages):
    result = analyze_messages(sample_messages)

    assert len(result["tasks"]) > 0


def test_analyzer_detects_decisions(sample_messages):
    result = analyze_messages(sample_messages)

    assert len(result["decisions"]) > 0


def test_task_records_have_expected_fields(sample_messages):
    result = analyze_messages(sample_messages)

    for task in result["tasks"]:
        assert isinstance(task, dict)
        assert "description" in task
        assert "owner" in task
        assert "deadline" in task
        assert "status" in task
        assert "evidence" in task
        assert isinstance(task["evidence"], list)


def test_decision_records_are_not_empty(sample_messages):
    result = analyze_messages(sample_messages)

    for decision in result["decisions"]:
        assert decision is not None
        assert str(decision).strip()


def test_summary_is_generated(sample_messages):
    analysis = analyze_messages(sample_messages)
    summary = build_summary(analysis)

    assert summary is not None
    assert str(summary).strip()


def test_empty_conversation_does_not_crash():
    result = analyze_messages([])

    assert isinstance(result, dict)
    assert result["message_count"] == 0
    assert result["tasks"] == []
    assert result["decisions"] == []
