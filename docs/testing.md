# Testing

Use the repository wrapper on Windows:

```powershell
scripts\validation\test_all.ps1
```

Focused STEP tests cover extensions and magic, unit conversion, legal/stable names, line/arc/cylinder
axis candidates, degenerate axes, mass distribution, inertia validity, fixed/revolute/prismatic
serialization, dynamics, XML escaping, cycles, safe ZIP extraction, relative meshes and versioned
workspace recovery.

Frontend checks are:

```powershell
pnpm --dir web/frontend type-check
pnpm --dir web/frontend lint
pnpm --dir web/frontend test
pnpm --dir web/frontend build
```

The optional upstream adapter is not downloaded by tests and no external model checkout is required.
