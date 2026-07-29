# Transform coordinate spaces

URDF Joint origins are persisted in the parent-link frame. The editor therefore defaults to **Parent**. **Local** is equivalent for a Joint-origin edit and is available as an explicit display choice. World-space numeric entry is shown but disabled in this release because writing world coordinates without resolving the complete current kinematic chain would be unsafe. Three.js gizmo world/local mode remains available for interactive manipulation and converts through the selected parent matrix before committing.
