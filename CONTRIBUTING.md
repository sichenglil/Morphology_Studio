# Contributing to Morphology Studio

Use GitHub Issues for confirmed bugs and proposals. Never attach confidential robot models, tokens, private paths, or workspaces. Security reports must follow [SECURITY.md](SECURITY.md).

## Development setup

Windows PowerShell:

```powershell
./scripts/setup_dev.ps1
./scripts/test_all.ps1
```

Linux/macOS:

```bash
./scripts/setup_dev.sh
./scripts/test_all.sh
```

Create a focused branch, add tests, and open a pull request against `main`. Use imperative Conventional Commit-style subjects such as `fix: reject unsafe export paths`. Run Python, frontend, E2E, and documentation checks appropriate to the change.

Python uses Ruff and type annotations; frontend code uses strict TypeScript, ESLint, Vitest, and Playwright. Core code must stay robot-agnostic and use `pathlib.Path`. Add dependencies only when their maintenance and license costs are justified. Record copied or modified third-party material in `THIRD_PARTY_NOTICES.md` and `.reuse/dep5`.

Screenshots must come from the current application, use generic examples, contain no private paths, and include reproducible capture steps. Never commit upstream model repositories, large meshes, user workspaces, generated output, `.env` files, credentials, or build caches.
