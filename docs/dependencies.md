# Dependencies

Runtime: PyYAML. Web mode: FastAPI and Uvicorn. Desktop mode: web dependencies plus pywebview. Optional mesh inspection: trimesh. Development: pytest, coverage, Ruff, MkDocs; frontend packages are locked by pnpm.

Python support is `>=3.9,<3.14`. Frontend support is Node 20–24 and pnpm 10–11, with CI on Node 22 and pnpm 11.9.0. PyInstaller is a build tool installed by the desktop build script. Xacro and Isaac integrations remain optional/environment-dependent. See `project/THIRD_PARTY_NOTICES.md` for license attribution.
