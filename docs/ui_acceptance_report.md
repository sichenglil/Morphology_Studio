# UI acceptance report

Local browser acceptance is performed at 1440×900 against the production Vue build served by the
loopback API. Screenshots are stored under `build/ui/current/`.

Verified in this phase: viewport-first editor layout, model tree, inspector region, bottom dock,
UR5e real mesh loading (13 links/12 joints), HX5 right-hand real mesh loading (27 links/26 joints),
combined model loading (40 links/39 joints), joint controls, validation results (0 errors/6 warnings
for HX5), local environment statuses, and responsive desktop sizing.

Screenshots:

- `build/ui/current/empty_editor.png`
- `build/ui/current/ur5e_loaded.png`
- `build/ui/current/hx5_loaded.png`
- `build/ui/current/ur5e_hx5_assembled.png`
- `build/ui/current/joint_controls.png`
- `build/ui/current/validation_panel.png`

Playwright passed three production-build checks: layouts at 1440×900 and 1920×1080, plus real UR5e
loading. The supplied FlexPhysics trials page was not accessible, so no visual equivalence is claimed.
Morphology Studio is an original interface aligned at the information-architecture level.
