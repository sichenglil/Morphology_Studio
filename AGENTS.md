# Repository guidance

- Keep `models/ur_description` and `models/robotis_hand` source trees read-only.
- Core modules must remain robot-agnostic; robot-specific names belong only in tests, examples, and acceptance configurations.
- Use `pathlib.Path` for filesystem paths and emit portable forward-slash resource URIs.
- Generated files belong in `build/`, `generated/`, or a user workspace.
- Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` on this workstation because an unrelated global pytest plugin stalls collection.
- Never push automatically.
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
