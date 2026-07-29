# Repository guidance

- This repository is the active standalone Morphology Studio development location.
- Never write Morphology Studio application source back to the legacy `Morphology-Conditioned` archive.
- The legacy directory is only an initial-file, source-model, and processed-model archive.
- Never commit upstream model repositories, user models, workspaces, or generated results here.
- Core code must not hard-code the legacy workspace or any machine-specific absolute path.
- Tests use temporary directories or small generic fixtures, never a required external model checkout.
- Keep the GitHub repository PRIVATE unless the user explicitly requests a visibility change.
- All future commits belong to this repository; never force-push.

- Treat externally selected `ur_description` and `robotis_hand` source trees as read-only.
- Core modules must remain robot-agnostic; robot-specific names belong only in tests, examples, and acceptance configurations.
- Use `pathlib.Path` for filesystem paths and emit portable forward-slash resource URIs.
- Generated reports and temporary files belong in `artifacts/`; `build/` and `dist/` are disposable packaging directories, while `release/` is the only deliverable tree.
- Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` on this workstation because an unrelated global pytest plugin stalls collection. Use `scripts/validation/test_all.ps1` for the complete suite and `project/build_exe.bat release` for a verified clean release build.
- Never push without an explicit user request.
- This is a generic robot model tool; UR5e and HX5 are examples and acceptance data only.
- This workstation has no ROS 2, Isaac Sim, or Isaac Lab. Do not create remote acceptance flows.
- Only locally executed results count as PASS; unavailable capabilities are `NOT_AVAILABLE_LOCAL`.
- The default processing mode is `assisted`; low-confidence recommendations require confirmation.
- Every completed feature needs a real local test.
- Performance work requires GitHub pre and post snapshots in a PRIVATE repository through the independent `github-backup` remote.
- Snapshot workflows must preserve `origin`, include non-ignored uncommitted/untracked files, scan sensitive filenames, and verify exact local restoration.
- Never use force push for snapshots or upload tokens, `.env`, keys, certificates, credentials, or secrets.
- A failed pre snapshot blocks performance edits; a failed post snapshot blocks completion.
- Desktop mode must work when `sys.stdout` and `sys.stderr` are `None` and must not depend on console logging.
- Do not use `git reset --hard` or `git clean -fd`.
