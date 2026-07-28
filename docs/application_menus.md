# Application menus

- File: new workspace, open workspace YAML, save workspace YAML, import model, export.
- Edit: undo, redo, copy/paste/reset the selected transform.
- View: focus/fit, six orthographic directions, grid and Collision visibility. Performance diagnostics are explicitly disabled unless the app is launched with `?debugPerformance=1`.
- Tools: validate, create an assembly connection, and export URDF. Opening a host log directory is visibly disabled in browser mode.

Commands share one ID catalog and dispatcher. Unavailable commands show contextual disabled states instead of silently doing nothing. Menu popups are teleported and do not participate in the toolbar's overflow or Three.js event region.
