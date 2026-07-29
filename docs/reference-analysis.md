# STEP reference analysis

## Evidence and license

The analysis used `Democratizing-Dexterous/step2urdf` commit `5c67a6768ce6767edf31aaa9e0737561363c315e`.
The upstream project is MIT licensed (copyright 2026 Democratizing Dexterity). Morphology Studio
does not vendor or copy its source. The optional checkout remains outside version control and the
integration invokes its public development command only.

## Useful upstream design

The reference application parses STEP locally with OpenCascade.js in a Comlink Web Worker. It
preserves compounds and solids in a tree, stores serialized triangle data independently of Three.js
objects, and separates selection, rendering, link/joint authoring, forward kinematics, inertia and
export. Circular/cylindrical and straight-edge features provide candidate joint axes. Export resets
the mechanism to its rest pose, transforms mesh vertices into link-local coordinates, generates
binary STL files in a worker, serializes URDF and downloads a ZIP.

This design is particularly valuable for privacy and responsiveness: CAD bytes remain local, heavy
geometry work stays off the UI thread, progress is explicit and workers/scene resources have defined
disposal paths.

## Existing Morphology Studio capability

Morphology Studio already has a generic Python robot model, URDF/Xacro import, resource resolution,
assembly, validation, portable packaging, a Three.js viewport, selection/highlighting, transform
editing, live joint motion and workspace persistence. Before this change it recognized `.step` and
`.stp`, but no importer was registered; directory analysis could recommend a STEP entry that always
failed during execution. The old helper could start a checkout but the UI could not discover it or
consume its output.

## Adopted design

- Keep CAD tessellation and semantic authoring in the separately installed upstream application.
- Discover it through `MORPHOLOGY_STEP2URDF_PATH`; never hard-code a workstation path.
- Expose adapter status and launch through CLI and the local desktop API.
- Explain the interactive boundary when a raw STEP file is selected.
- Safely import the exported URDF ZIP, reject path traversal, cache by content hash and retain
  relative mesh references.
- Provide independent, testable helpers for STEP unit conversion, stable occurrence IDs, legal URDF
  names, feature/axis candidates, mass distribution and inertia validation.
- Preserve and export joint damping/friction and add one-click portable ZIP export.

## Not adopted

The upstream Vue application and OpenCascade WASM bundle are not embedded. Doing so would duplicate
the current renderer/state architecture, materially enlarge the desktop build and create two
conflicting robot documents. Fully automatic STEP-to-URDF conversion is also intentionally rejected:
CAD topology alone cannot safely infer mechanism semantics, parent/child links or motion limits.
Low-confidence geometry must remain a suggestion requiring user confirmation.

## Architecture difference

Upstream is a browser-only CAD authoring application whose source of truth is tessellated STEP
geometry and Pinia state. Morphology Studio is a desktop-hosted editor whose source of truth is a
format-neutral Python `RobotModel`. The adapter boundary is consequently an exported, portable URDF
package rather than shared in-memory JavaScript objects.

## Known gap

Raw STEP is not converted headlessly. The optional editor must be installed, the user must define
the kinematic semantics, and the resulting ZIP must be selected in Morphology Studio. This is an
experimental assisted workflow, not native STEP export.
