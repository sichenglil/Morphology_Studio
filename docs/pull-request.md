## Background

Morphology Studio detected STEP files but could neither guide conversion nor load step2urdf output.

## Reference and license

The design was reviewed against `Democratizing-Dexterous/step2urdf` at commit `5c67a67` (MIT). No
upstream source or assets are vendored.

## Changes

- Optional local adapter discovery, status and launch via CLI/API/UI.
- Assisted raw STEP workflow and safe step2urdf ZIP round trip.
- Geometry/axis, unit, naming, stable ID, mass and inertia helpers.
- Joint dynamics import/validation/export and portable ZIP export.
- Versioned workspace persistence, tests and architecture/user documentation.

## Compatibility and rollback

Existing URDF/Xacro paths and workspace fields remain valid; missing workspace schema versions map to
version 1. Roll back by reverting the commits in this PR. The adapter is optional and never bundled.

## Testing

Local verification completed on Windows/Python 3.9:

- Ruff check and format check: passed.
- Pytest: 55 passed; coverage 68%.
- Vue TypeScript and ESLint: passed.
- Vitest: 20 passed.
- Vite production build: passed (existing large-chunk warning remains).
- Playwright: 13 passed, 2 media-capture tests skipped by their existing conditions.
- Documentation links/format, strict MkDocs, REUSE and repository health: passed.

See `docs/testing.md` and the PR checks.

## Known limitations

Raw STEP conversion remains interactive because link/joint semantics cannot safely be inferred from
CAD topology. UI screenshots are unchanged except for the import/export dialog controls.
