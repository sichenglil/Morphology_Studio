# Joint rendering performance audit

## Before optimization

The `el-slider` `input` event called `store.moveJoint`, which immediately sent `PATCH /api/joints/{name}`.
Every successful response mutated `scene.joints[].value`. `RobotViewport` watched the complete scene with
`deep: true`, so each value caused `rebuild()`: the robot group was removed, every Link and material was
created again, every DAE/STL loader ran again, and FK was recomputed for every Joint. A permanent RAF loop
also rendered while idle. The backend appended one file-log entry per intermediate value.

Consequences for N slider events were N backend requests, N complete scene rebuilds, approximately
N × visual-count mesh loads, N full-tree FK passes, and N log writes. Structural validation, workspace YAML
writes, URDF export and parsing were not on this path. Vue updated all slider consumers because live values
were stored inside the deep scene manifest. The repeated asynchronous loaders were the main latency and
allocation source; the request/render/rebuild feedback loop also allowed stale builds to overlap.

## After optimization

`input` updates a `JointRuntime.motionObject` through an O(1) Map lookup. Three.js propagates only its child
subtree and a single `RenderScheduler` coalesces all same-frame invalidations. `change` queues one batch
commit after an 80 ms merge window. The scene manifest, ModelTree, meshes, materials and static Joint origin
objects remain stable. Full validation and workspace persistence are not invoked by preview or commit.

Runtime counters cover frame/FK/render time, draw calls, triangles, pending updates, backend commits, scene
rebuilds, mesh loads and workspace saves. `?debugPerformance=1` shows them without enabling diagnostics by
default. Resource cache entries are reference-counted and released when the model runtime is replaced.
