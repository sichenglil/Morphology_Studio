# Performance troubleshooting

- Rising mesh loads: check that model generation, not joint values, drives runtime rebuilding.
- Vue stalls: do not place Scene/Object3D/Geometry/Material in reactive stores or deep-watch a scene manifest.
- Excess requests: slider `input` must emit preview; only `change` emits commit.
- Excess draw calls: hide collision geometry and per-Link helpers; never merge across movable Links.
- High frame time: select Performance quality and compare render time with FK time in the diagnostics panel.
- Memory growth: ensure runtime disposal releases cached resources and event handlers; do not dispose shared
  resources during a joint update.
