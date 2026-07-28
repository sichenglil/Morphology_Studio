# Menu and precise transform acceptance

The menu root cause was four static labels with no interaction implementation. No Canvas overlay, pointer-events rule, overflow clipping, or pywebview drag region covered them. The replacement uses teleported Element Plus dropdowns and centralized command IDs.

The real two-link fixture began with `parent_joint.origin = xyz(0.1, 0, 0), rpy(0, 0, 0)`. Through the inspector, X was entered as `25 mm` and Yaw as `15 deg`. One Apply request produced revision 1 and backend values `xyz(0.025, 0, 0)` and `rpy(0, 0, 0.2617993877991494)`. Saved workspace reopening preserved the values. URDF export contained the same values; reimport/reopen error was below `1e-9`.

Playwright opened File/Edit/View/Tools, verified the pointer hit target, Escape closure, ImportWizard execution, precise inputs, local preview, commit, workspace save/open, and URDF serialization. Screenshots are in `build/ui/acceptance/menu-and-numeric-editor/`.

Known limits: native Windows DPI 125%/150% cannot be switched by browser automation. World-space numeric entry and matrix import are intentionally disabled pending a full frame-conversion editor. Physical gizmo dragging remains covered by the existing transform acceptance; this stage verifies the numeric-to-scene path directly.
