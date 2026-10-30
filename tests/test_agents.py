from app.agents.team import DISCLAIMER

def test_disclaimer_is_present():
    assert "not a diagnosis" in DISCLAIMER.lower()

def test_team_module_exposes_build_function():
    from app.agents.team import build_medical_team
    assert callable(build_medical_team)
