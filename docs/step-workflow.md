# Embedded STEP-to-URDF workflow

## Import inside the desktop application

1. Start `MorphologyStudio.exe` and choose **Import model**.
2. Select a `.step` or `.stp` file. Choose **Parse STEP**.
3. Wait while the bundled OpenCascade WebAssembly engine tessellates the file in a Worker.
4. Review every solid's Link name. For each non-root solid, choose an earlier parent, joint type and
   joint axis. The default is a fixed child of the first solid.
5. Choose **Import and display**, inspect the model and preview movable joints.
6. Run validation, correct transforms or semantics, then export URDF, a portable directory or ZIP.

No external step2urdf checkout, Node.js installation, environment variable or network connection is
required by the packaged application. Existing step2urdf URDF ZIP files can still be imported.

## Units, files and privacy

- STEP geometry is treated as millimetres and represented in URDF with mesh scale `0.001`.
- Generated binary STL files are cached under `%LOCALAPPDATA%\MorphologyStudio\step_imports` using a
  content hash. Set `MORPHOLOGY_STEP_CACHE` only for development/testing overrides.
- CAD bytes are served only by the loopback application and parsed locally in the bundled Worker.
- Imports are limited to 500 MiB source files, 512 solids and 250 MiB of generated STL data.

## Limitations and troubleshooting

- A STEP file does not normally encode URDF joint semantics, limits, mass or inertia. Review the
  assisted result and add physical parameters before simulation.
- OpenCascade WASM is about 50 MB uncompressed and is loaded only for STEP import.
- Very large assemblies can exceed WebView2 memory. Simplify them in CAD or import subassemblies.
- **No triangulatable solids** means the file contains unsupported, empty or damaged topology.
- If Windows lacks WebView2, install the Microsoft Edge WebView2 Runtime before starting the EXE.
