# UI architecture

The formal client lives in `web/frontend` and uses Vue 3, TypeScript, Vite, Element Plus, Pinia and
Three.js. Its editor shell has a workflow toolbar, searchable model tree, central real-time viewport,
context inspector, joint/validation/log dock, and status bar. The Pinia editor store coordinates tree,
viewport, inspector, joint values, validation, assembly and task messages.

Three.js builds a robot-agnostic world-transform graph from links and joints. URDF RPY is evaluated as
`Rz(yaw) * Ry(pitch) * Rx(roll)`, and the editor uses a Z-up camera. Meshes are fetched only through
opaque registered API URLs. Collision STL is preferred for a stable editable view; visual geometry is
used when collision geometry is absent.
