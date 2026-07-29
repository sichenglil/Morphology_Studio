# STEP-to-URDF workflow

## Install the optional adapter

```powershell
git clone https://github.com/Democratizing-Dexterous/step2urdf.git external/step2urdf
cd external/step2urdf
pnpm install
$env:MORPHOLOGY_STEP2URDF_PATH = (Get-Location).Path
```

The adapter is MIT licensed and is not part of the Morphology Studio installation. Check status or
start it with:

```powershell
morphology-tool step-adapter status
morphology-tool step-adapter launch
```

## Convert and return

1. Select a `.step` or `.stp` file in the Morphology Studio import dialog.
2. Start the detected local adapter.
3. In step2urdf, inspect the assembly tree, bind solids to links, define parent/child joints, confirm
   axes and limits, then configure total/link mass and inertia.
4. Export the URDF ZIP from step2urdf.
5. Choose **Select exported ZIP** in Morphology Studio. The package is checked for unsafe paths,
   extracted to a content-addressed local cache and loaded with its relative STL resources.
6. Validate the model, preview joint motion, correct warnings, and export URDF, a portable directory,
   or a portable ZIP.

STEP lengths are normalized to URDF metres. Geometry axes are suggestions only; degenerate and empty
results are rejected, and no joint is silently created.

## Troubleshooting

- `Set MORPHOLOGY_STEP2URDF_PATH`: point it at a checkout containing `package.json`.
- `pnpm was not found`: install a supported Node.js/pnpm toolchain.
- `Run pnpm install first`: install the adapter's own dependencies in its checkout.
- `Unsafe path in STEP export package`: the ZIP contains traversal entries and is rejected.
- The browser opens before the adapter is ready: wait for Vite to finish, then refresh its local URL.
