from pathlib import Path

SCRIPT = Path("scripts/github_snapshot_backup.ps1")


def test_snapshot_script_has_private_remote_and_restore_guards():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "PRIVATE" in text
    assert "github-backup" in text
    assert "--include-untracked" in text
    assert "stash', 'pop', '--index".replace(" ", "") in text.replace(" ", "")
    assert "BACKUP_RESTORE_VERIFICATION_FAILED" in text
    assert "BACKUP_BLOCKED_SENSITIVE_FILES" in text
    assert "--force" not in text
    assert "set-url" not in text
    assert "push','origin" not in text


def test_snapshot_script_covers_required_fingerprints_and_collision_handling():
    text = SCRIPT.read_text(encoding="utf-8")
    for required in ("before-status.txt", "before-working.diff", "before-cached.diff", "SHA256"):
        assert required in text
    assert "REMOTE_NAME_CONFLICT" in text
    assert "NewGuid" in text
    assert "ls-remote','--exit-code" in text
