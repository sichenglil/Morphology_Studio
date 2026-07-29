# Architecture

```mermaid
flowchart LR
  UI[Vue + Three.js] -->|JSON / local HTTP| API[FastAPI]
  API --> Model[RobotModel in memory]
  Import[URDF / Xacro / MJCF importers] --> Model
  Model --> Validate[Validators]
  Model --> Export[URDF / MJCF / package exporters]
  Desktop[pywebview shell] --> API
```

`RobotModel` is the source of truth. Importers normalize external formats, the API exposes controlled operations, and the renderer maintains a runtime index for incremental updates. File selection is isolated in the desktop bridge; no arbitrary command bridge exists.
