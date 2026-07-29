# Desktop architecture

Morphology Studio uses a pywebview native Windows window backed by WebView2. A loopback-only Uvicorn
server runs in a managed background thread and serves the Vue production assets and robot-agnostic
FastAPI endpoints. Closing the native window sets `server.should_exit` and joins the server thread.

The Python `RobotModel` remains the source of truth. The Vue client receives scene manifests and
opaque resource URLs; it never reads arbitrary local paths. Joint edits are validated by the API and
recorded in the session change log. Source models remain read-only.

Transform editing uses a proxy `Object3D` so kinematic world matrices are never confused with serialized
local origins. Raycaster hits carry stable `entityType/entityId/linkId` metadata. During a drag the proxy
updates only the rendered scene; `dragging-changed=false` creates one revision-checked API transaction.
The transaction mutates the canonical model, truncates any redo branch, and returns a fresh scene manifest.
Undo and redo apply the stored before/after values and also advance the revision. Workspace YAML persists
the replayable edits without changing imported source trees.
