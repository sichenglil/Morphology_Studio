## Background

Morphology Studio previously required a separately installed step2urdf editor and a manual URDF ZIP
round trip. The packaged EXE could detect STEP but could not open it directly.

## Reference and license

The Worker design was reviewed against `Democratizing-Dexterous/step2urdf` commit `5c67a67` (MIT).
The reduced and modified Worker is attributed in DEP5 and third-party notices. OpenCascade.js is a
locked `LGPL-2.1-only` runtime dependency whose WASM is bundled for offline operation.

## Changes

- Lazy, embedded OpenCascade.js STEP parsing in a Web Worker.
- Direct `.step`/`.stp` import with Link, parent, joint type and axis confirmation.
- Validated binary STL generation and content-addressed user cache.
- Existing `RobotModel`, viewport, validation and export pipeline reused without a second editor.
- Old external adapter launcher, CLI command and helper script removed.
- Existing step2urdf URDF ZIP imports remain backward-compatible.

## Testing

Tests cover binary STL validation, name safety, parent ordering, joints, units, cache paths, API routes
and previous ZIP compatibility. A public 50 KB STEP sample was also parsed through the real local GUI:
the bundled WASM produced one solid, loaded it into the 3D workspace and emitted no console errors.

## Known limitations

Kinematic semantics are interactive because STEP geometry does not reliably encode them. OpenCascade
WASM adds about 50 MB uncompressed, loads only on STEP import and remains subject to WebView2 memory.
