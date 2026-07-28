# Rendering performance

Drawing a new frame after a joint changes is required; reconstructing the scene is not. The editor keeps
geometry, material, hierarchy and static origins alive, and updates only Joint Motion.

Open `/?debugPerformance=1` to show diagnostics. Quality presets cap device pixel ratio at 1.0
(Performance), 1.5 (Balanced) or 2.0 (Quality); shadows remain off except in Quality. If `sceneRebuilds` or
`meshLoads` rises while dragging a slider, treat it as a regression. Draw calls should remain stable.

Run `pnpm --dir web/frontend test` for the 1000-update architecture benchmark and Playwright for real WebGL
coverage. FPS varies by GPU and CI load, so tests enforce no rebuild, no reload, no preview request and RAF
coalescing while reports retain observed timing.
