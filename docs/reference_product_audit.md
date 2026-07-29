# Reference product audit

## Scope and evidence

This audit was performed from the public `Democratizing-Dexterous/step2urdf` repository cloned under
`external/reference_step2urdf` for read-only study. The FlexPhysics trials URL was also checked on
2026-07-28, but the page did not return a usable document in the available browser or web reader;
no unseen structure is inferred below.

## step2urdf

The public application is a Vue 3 and TypeScript Vite application. Its dependencies include Element
Plus, Pinia, Vue Router, Three.js, Monaco Editor, JSZip, Comlink/Web Workers, OpenCascade.js and
`three-mesh-bvh`.

Its editor is organized around a full-height Three.js canvas. A global toolbar controls loading,
camera fitting, axes, grid, opacity, measurement, statistics and the model tree. A fixed URDF tree
occupies the left side, the viewport remains central, and a contextual URDF property panel occupies
the right. Floating joint controls and joint creation workflows overlay the viewport. A bottom status
bar reports solid, robot, link, joint and selection state.

The main workflow is: load a CAD file, inspect the solid hierarchy, bind solids to links, create and
configure joints, inspect forward kinematics, then serialize/export URDF. Pinia stores own the active
document and selection; rendering, selection, kinematics, inertia and export are separated into core
classes and workers.

We borrow only the general information architecture: viewport-first layout, synchronized hierarchy
and selection, contextual inspectors, explicit joint controls, task progress, and staged import/export.
We do not copy source, logos, marketing text, visual branding, or assets. No reference code is included
in Morphology Studio, so no license notice is required for copied code.

## FlexPhysics

The supplied trials page could not be rendered or read in the available local browser session and its
direct web endpoint returned no usable page. Consequently, this implementation makes no claim about
its precise layout and does not copy any FlexPhysics code, brand, assets, text, icons, or styling.

## Product gap before this phase

The previous product was a FastAPI-served single HTML form surface around CLI commands. It had no
native window lifecycle, formal document state, synchronized model tree, contextual inspector,
joint/FK panel, assembly interaction, or true Three.js scene. The new architecture retains the tested
robot-agnostic Python core and introduces a native desktop host plus a Vue/TypeScript editor client.
