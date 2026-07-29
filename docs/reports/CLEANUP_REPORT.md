# Cleanup Report

## Second-pass root consolidation

- Moved `_archive` to `artifacts/archive`; uncertain historical files remain recoverable.
- Moved development logs from root `logs` to `artifacts/logs`. Frozen releases still
  create `logs` beside the executable for end-user diagnostics.
- Moved `packaging/MorphologyStudio.spec` to
  `scripts/build/packaging/MorphologyStudio.spec` and updated its project-root lookup.
- Reduced the functional root directories from 15 to 12 without moving tool-required
  metadata such as `.github`, `.reuse`, `LICENSES`, or the user-facing `release` folder.

## Safety and rollback

The complete pre-change copy is
`G:\Code_Programs\VscodeProjects\Robot\Morphology_Studio_backup_structure_20260729_223953`.
Robocopy copied 28,351 files (552.28 MB) with zero failed files and zero mismatches.
Rollback is performed by closing the application and restoring that directory. `.git` internals
were not edited by this cleanup.

## Deleted generated content

- Python `__pycache__`, `*.pyc`, pytest/Ruff caches, `.coverage`, and MkDocs `site` output.
- Temporary GIF frames, temporary smoke-test working directory, and temporary logs.
- PyInstaller `build` cache and duplicate `dist` output, but only after release verification.
- Empty legacy `configs`, `scripts/dev`, and `scripts/migrations` directories.

## Moves and merges

- `configs/package_maps/local_models.yaml` ->
  `config/models/package_maps/local_models.yaml`; all active references were updated.
- Root governance documents -> `docs/governance`.
- `CHANGELOG.md` -> `docs/development/CHANGELOG.md`.
- Build documentation and reports -> `docs/packaging` and `docs/reports`.
- Generated report screenshots -> `artifacts/screenshots/acceptance`.
- Scripts were classified under `scripts/build`, `scripts/render`, `scripts/validation`, and
  `scripts/maintenance`; the deprecated build forwarder was archived under
  `artifacts/archive/legacy_scripts`.
- Historical and uncertain files are consolidated under `artifacts/archive`.

## Decisions

- Web is active: Python embeds the Vite output and the desktop depends on it.
- MkDocs is active: strict documentation build is part of the validation suite.
- REUSE is active: `.reuse`, `LICENSES`, and license texts remain at the root; lint passes.
- `src/morphology_toolkit` is an established standard src-layout package and was not renamed.
- `CITATION.cff` remains at the root because this is a research/robotics project.
- Only `assets/robot_models/ur5e_hx5_right` and its preview resources remain active.

## Path and build fixes

- Updated imports, CI commands, tests, README commands, documentation links, package-map paths,
  and moved-script project-root calculations.
- Removed runtime references to machine-specific project/model source paths.
- Fixed `project/build_exe.bat` to use `call pnpm` (required for control to return from `pnpm.cmd`).

## Root helper consolidation

- Added `project/` for developer-facing launch, build, dependency, entry-point, and
  third-party notice files.
- Moved `build_exe.bat`, `run_app.bat`, `desktop_entry.py`, `requirements.txt`,
  `requirements-dev.txt`, and `THIRD_PARTY_NOTICES.md` into that directory.
- Kept repository-discovery files in the root so GitHub, Git, Python packaging,
  pnpm, MkDocs, REUSE, and Codex continue to discover their configuration normally.
- Release builds now clean old intermediates, test, verify resources, build, prepare and smoke-test
  the release, then remove `build` and `dist`.

## Validation

Python installation/import, Ruff, 43 pytest tests, resource verification, README checks, MkDocs
strict build, REUSE lint, repository health, source API health, desktop tests, PyInstaller build,
and packaged EXE smoke testing passed.

## Known limitations

- A terminal policy rejected a background-process source probe; equivalent in-process API health
  and desktop creation tests were used instead.
- PyInstaller emits a non-fatal optional `tzdata` warning.
