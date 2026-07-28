# Link panel scrolling audit

## Finding

The model data was not truncated. `loadModel()` assigns the complete scene response to the Pinia editor store, `ModelTree` filters the full `scene.links` array, and no `slice`, limit, or abbreviated tree API sits in that path. The 100-link acceptance fixture produced 100 links in the backend scene response, 100 in Pinia, 100 filtered links, and 100 rendered link buttons.

The defect was a height-containment failure. The sidebar had `overflow: hidden`, while the tree content did not form a shrinkable flex/grid chain and Links had no dedicated scrolling viewport. Growing Links content was therefore clipped by the sidebar. Resources and Semantics were static tab labels rather than accessible content regions. This model tree is embedded directly in the workbench, not in an Element Plus Dialog, so Dialog body overrides are not applicable.

## Measured data path and browser state

| Measurement | Result |
|---|---:|
| Test model links | 100 |
| Backend scene links | 100 |
| Pinia links | 100 |
| Filtered links | 100 |
| DOM link rows (100-link mode) | 100 |
| Links `clientHeight` at 1440×900 | 247 px |
| Links `scrollHeight` at 1440×900 | 3504 px |
| Computed `overflow-y` | `auto` |
| Wheel receiver | `.links-scroll` under the pointer |
| Sidebar wheel `preventDefault` | none |
| Three.js controls target | renderer canvas only |

Development builds emit one compact count diagnostic after mounting. Production builds emit none.

## Resolution

The sidebar is now a bounded column with `height: 100%`, `min-height: 0`, and `overflow: hidden`. `ModelTree` is a four-row grid using `minmax(0, 1fr)` for Links and a bounded Joint region. Each list region has exactly one scrolling child using `min-height: 0`, `overflow-y: auto`, `overscroll-behavior: contain`, and stable scrollbar gutter.

Resources and Semantics use the existing tab concept, with independent scroll containers. `v-show` preserves the model tree instance and its scroll position while switching tabs. Selection uses stable IDs and nearest-item scrolling; lists above 200 links use fixed-row virtualization measured by `ResizeObserver`.

There are no global wheel listeners. OrbitControls remains bound only to the canvas, so sidebar wheel events do not zoom the camera while canvas wheel events still do.
