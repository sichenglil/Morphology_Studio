# STEP reference analysis

## Evidence and license

The implementation was reviewed against `Democratizing-Dexterous/step2urdf` commit
`5c67a6768ce6767edf31aaa9e0737561363c315e`. The upstream project is MIT licensed (copyright 2026
Democratizing Dexterity). A reduced STEP tessellation Worker was adapted under that license;
attribution is recorded in `project/THIRD_PARTY_NOTICES.md` and `.reuse/dep5`.

## Adopted design

The reference application demonstrated that OpenCascade.js can read and tessellate STEP locally in a
Web Worker. Morphology Studio adopts that boundary without copying the upstream application:

- bundle OpenCascade.js and load its WASM lazily for `.step` and `.stp` files;
- keep heavy parsing off the Vue UI thread;
- transfer typed triangle buffers instead of OpenCascade or Three.js objects;
- let the existing import dialog confirm link names, parent relationships, joint types and axes;
- generate validated binary STL resources in a content-addressed user cache;
- create the existing Python `RobotModel` and reuse its renderer, validation and exporters;
- retain safe import compatibility for existing step2urdf URDF ZIP packages.

## Deliberately not copied

The upstream router, Pinia stores, Element Plus application, Three.js scene, Monaco editor, export UI,
measurement tools and unrelated dependencies are not included. This avoids two conflicting model
documents and keeps Morphology Studio's existing renderer and editing architecture.

Fully automatic STEP-to-URDF semantic inference is also rejected. CAD topology alone cannot safely
identify robot parent/child relationships, joint types, limits, mass or inertia. Geometry becomes
link candidates; mechanism semantics remain an explicit assisted decision.

## Architecture difference

Upstream is a browser CAD authoring application whose working state is tessellated STEP geometry.
Morphology Studio is a desktop-hosted robot editor whose source of truth is a format-neutral Python
`RobotModel`. Its integration boundary is therefore typed triangle buffers converted to validated
binary STL, followed by the normal model pipeline.

## Current limitations

Raw STEP now opens directly in the EXE, but the user must define kinematic semantics. OpenCascade WASM
adds approximately 50 MB uncompressed and very large assemblies are constrained by WebView2 memory.
This is an embedded assisted workflow, not a claim that CAD topology alone describes a robot.
