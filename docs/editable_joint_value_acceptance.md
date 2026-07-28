# Editable joint value acceptance

- Model: local packaged UR5e (`build/packages/ur5e/robot.urdf`), 12 joints, 6 scalar movable joint inputs.
- Tested joint: `shoulder_pan_joint`; values included `1.`, `-0.5 rad`, degree display, and an over-limit value.
- Synchronization: valid draft text updated the slider and indexed Three.js joint runtime; Enter produced one backend commit; no per-character request occurred.
- Performance: existing browser benchmark remained at one initial scene rebuild with no rebuild during joint edits.
- Pose: named pose save, zero, and batch load were exercised. Pose load sends one batch joint-state request.
- Local support: browser, pywebview, and PyInstaller use the same compiled frontend. ROS 2 and Isaac remain `NOT_AVAILABLE_LOCAL`.

Screenshots are in `build/ui/acceptance/editable-joint-values/`.
