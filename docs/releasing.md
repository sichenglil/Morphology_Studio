# Releasing

1. Update the version in `pyproject.toml`, `src/morphology_toolkit/__init__.py`, `web/frontend/package.json`, and `CITATION.cff`.
2. Move relevant changelog entries into the release section.
3. Run all tests, documentation checks, and the Windows desktop build.
4. Commit, create a signed `vX.Y.Z` tag, and push it after review.
5. Verify the Release workflow, checksums, release notes, and uploaded directory archive.

This preparation does not create a release automatically.
