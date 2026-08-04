from pathlib import Path

from radeonvla.submission_audit import audit_project

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_current_release_structure_passes_pre_release_audit() -> None:
    result = audit_project(PROJECT_ROOT)
    assert result.errors == []
    assert result.warnings


def test_current_release_structure_is_not_final() -> None:
    result = audit_project(PROJECT_ROOT, final=True)
    assert not result.ok
    assert any("pre-release marker" in error for error in result.errors)
