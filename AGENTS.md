# Repository guidance

- Keep `models/ur_description` and `models/robotis_hand` source trees read-only.
- Core modules must remain robot-agnostic; robot-specific names belong only in tests, examples, and acceptance configurations.
- Use `pathlib.Path` for filesystem paths and emit portable forward-slash resource URIs.
- Generated files belong in `build/`, `generated/`, or a user workspace.
- Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` on this workstation because an unrelated global pytest plugin stalls collection.
- Never push automatically.

