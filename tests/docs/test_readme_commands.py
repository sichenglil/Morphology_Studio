from pathlib import Path

from scripts.validation.check_docs_links import check

ROOT = Path(__file__).resolve().parents[2]


def test_document_links_exist():
    assert check(ROOT) == []


def test_readme_commands_reference_real_entries():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for text, path in {
        "python project/desktop_entry.py": "project/desktop_entry.py",
        "./scripts/maintenance/setup_dev.ps1": "scripts/maintenance/setup_dev.ps1",
        "./scripts/validation/test_all.ps1": "scripts/validation/test_all.ps1",
        "LICENSE": "LICENSE",
        "backend-ci.yml": ".github/workflows/backend-ci.yml",
    }.items():
        assert text in readme
        assert (ROOT / path).exists()
