# Testing

Use the repository wrapper on Windows:

```powershell
scripts\validation\test_all.ps1
```

Focused STEP tests cover extensions and magic, unit conversion, legal/stable names, line/arc/cylinder
axis candidates, degenerate axes, mass distribution, inertia validity, fixed/revolute/prismatic
serialization, binary STL validation, parent ordering, direct-import caching, dynamics, XML escaping,
cycles, safe ZIP extraction, relative meshes and versioned workspace recovery.

Frontend checks are:

```powershell
pnpm --dir web/frontend type-check
pnpm --dir web/frontend lint
pnpm --dir web/frontend test
pnpm --dir web/frontend build
```

No external adapter or model checkout is required. For release acceptance, parse a small public or
locally generated STEP file through the desktop dialog and verify that the model reaches the viewport.
