# Maintainer guide

Keep changes focused, update tests and notices, run `./scripts/test_all.ps1`, and inspect `git diff --check`. Never commit user models or generated output. Review filesystem operations for traversal and overwrite behavior. Update Python, pnpm, CI, PyInstaller, and documentation together when changing dependencies or entry points.
