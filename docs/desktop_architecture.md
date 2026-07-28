# Desktop architecture

Morphology Studio uses a pywebview native Windows window backed by WebView2. A loopback-only Uvicorn
server runs in a managed background thread and serves the Vue production assets and robot-agnostic
FastAPI endpoints. Closing the native window sets `server.should_exit` and joins the server thread.

The Python `RobotModel` remains the source of truth. The Vue client receives scene manifests and
opaque resource URLs; it never reads arbitrary local paths. Joint edits are validated by the API and
recorded in the session change log. Source models remain read-only.
