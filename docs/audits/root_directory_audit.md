# Root directory audit

The baseline contained 37 visible project items including ignored caches and generated directories. Tracked root clutter consisted of the PyInstaller specification and the migration report.

Actions:

- **MOVE:** `MorphologyStudio.spec` to `packaging/windows/MorphologyStudio.spec`.
- **MOVE:** `MIGRATION.md` to `docs/maintainers/migration.md`.
- **MOVE:** optional conversion/model scripts to `scripts/dev/`.
- **MOVE:** deprecated Windows build forwarder to `scripts/migrations/`.
- **DELETE_AFTER_TEST:** duplicate `scripts/desktop_entry.py`; the root compatibility entry and package entry remain.
- **KEEP:** GitHub-standard governance, security, citation, license, changelog, and README files.
- **MOVED:** `desktop_entry.py` to `project/desktop_entry.py`; it remains a thin documented delegate to the package entry point.

Ignored `.coverage`, caches, `build`, `dist`, and `site` are local products rather than repository content. PyInstaller, documentation, CI, and script references were updated before verification.
