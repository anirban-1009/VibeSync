from app.logic.mood_parser import parse_mood


def test_parse_mood_study():
    result = parse_mood("I want study mode")
    assert result["target_energy"] == 0.3
    assert result["target_instrumentalness"] == 0.8


def test_parse_mood_party():
    result = parse_mood("Let's party hard")
    assert result["target_energy"] == 0.85
    assert result["min_tempo"] == 120


def test_parse_mood_chill():
    result = parse_mood("chill vibes")
    assert result["target_energy"] == 0.5
    assert result["target_valence"] == 0.5


def test_parse_mood_sad():
    result = parse_mood("feeling blue")
    assert result["target_valence"] == 0.2
    assert result["target_energy"] == 0.4


def test_parse_mood_happy():
    result = parse_mood("feeling good")
    assert result["target_valence"] == 0.8
    assert result["target_energy"] == 0.7


def test_parse_mood_unknown():
    result = parse_mood("random string")
    assert result == {}
