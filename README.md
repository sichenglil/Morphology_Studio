<div align="center">

# Morphology Studio

<p>A source-preserving desktop workspace for inspecting, editing, assembling, validating, and converting robot models.</p>

<p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a></p>

<p>
  <a href="https://github.com/sichenglil/Morphology_Studio/actions/workflows/backend-ci.yml"><img alt="Backend CI" src="https://github.com/sichenglil/Morphology_Studio/actions/workflows/backend-ci.yml/badge.svg"></a>
  <a href="https://github.com/sichenglil/Morphology_Studio/actions/workflows/frontend-ci.yml"><img alt="Frontend CI" src="https://github.com/sichenglil/Morphology_Studio/actions/workflows/frontend-ci.yml/badge.svg"></a>
  <a href="https://github.com/sichenglil/Morphology_Studio/actions/workflows/e2e.yml"><img alt="E2E" src="https://github.com/sichenglil/Morphology_Studio/actions/workflows/e2e.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue.svg"></a>
</p>


<p><strong>Version 0.1.0 · Alpha · ROS-free core · Optional ROS 2 and Isaac integrations planned</strong></p>

</div>

## Robot operation demo

The animation below records the packaged `ur5e_hx5_right` robot being loaded and operated inside Morphology Studio.

<p align="center"><img src="assets/previews/ur5e_hx5_right/robot.gif" width="960" alt="Operating UR5e with HX5 Right inside Morphology Studio"></p>

- The GIF is captured from the real application while loading the model and moving a joint.
- The application and EXE use the copied resources under `assets/robot_models/ur5e_hx5_right`.
- Running the application does not require the original Morphology-Conditioned project.
- Regenerate with `python scripts/generate_software_demo_gif.py`.

<a id="contents"></a>
<h2 align="center">Contents</h2>

<p align="center"><a href="#overview">Overview</a> · <a href="#features">Features</a> · <a href="#formats">Formats</a> · <a href="#requirements">Requirements</a> · <a href="#quick-start">Quick start</a> · <a href="#gallery">Gallery</a> · <a href="#architecture">Architecture</a> · <a href="#roadmap">Roadmap</a></p>

<a id="overview"></a>
<h2 align="center">Overview</h2>

Morphology Studio keeps the source model read-only while providing one workspace for model inspection and preparation. It is robot-agnostic: robot names, link names, joint counts, and package layouts are discovered from input data rather than embedded in core logic.

<table align="center">
<tr>
<td align="center"><strong>Source preserving</strong><br>Edits and generated files stay outside the original model.</td>
<td align="center"><strong>Robot agnostic</strong><br>Structure and resources are discovered from the input data.</td>
<td align="center"><strong>ROS-free workflow</strong><br>Expand Xacro and build portable packages with explicit package maps.</td>
</tr>
</table>

<a id="features"></a>
<h2 align="center">Feature modules</h2>

Each module below states its purpose, main action, input, output, maturity, and detailed guide.

<table align="center">
<thead><tr><th align="center">Module</th><th align="left">Purpose and operation</th><th align="left">Input → output</th><th align="center">Status</th><th align="center">Guide</th></tr></thead>
<tbody>
<tr><td align="center"><strong>Model Import</strong></td><td align="left">Open a file or scan a directory; confirm assisted low-confidence choices.</td><td align="left">URDF / Xacro / MJCF / directory → normalized model</td><td align="center">Stable / Beta by format</td><td align="center"><a href="docs/import_models.md">Import</a></td></tr>
<tr><td align="center"><strong>Model Tree & Viewport</strong></td><td align="left">Search large hierarchies and inspect resolved primitives and STL/DAE meshes in an interactive Three.js scene.</td><td align="left">Normalized model + assets → synchronized tree and 3D selection</td><td align="center">Stable</td><td align="center"><a href="docs/user_guide.md">User guide</a></td></tr>
<tr><td align="center"><strong>Joint Control</strong></td><td align="left">Preview motion with sliders or exact signed values, selectable units, precision, and limit feedback.</td><td align="left">Joint limits + value → posed robot</td><td align="center">Stable</td><td align="center"><a href="docs/joint_control.md">Joint control</a></td></tr>
<tr><td align="center"><strong>Transform Editing</strong></td><td align="left">Move or rotate selected objects with a gizmo or exact XYZ/RPY fields.</td><td align="left">Selection + transform → tracked model edit</td><td align="center">Beta</td><td align="center"><a href="docs/transform_editing.md">Transforms</a></td></tr>
<tr><td align="center"><strong>Assembly</strong></td><td align="left">Choose parent and child roots and create a generic fixed connection.</td><td align="left">Two models + pose → combined model</td><td align="center">Beta</td><td align="center"><a href="docs/assembly.md">Assembly</a></td></tr>
<tr><td align="center"><strong>Validation</strong></td><td align="left">Check names, topology, limits, resources, and export readiness.</td><td align="left">Current model → actionable errors and warnings</td><td align="center">Beta</td><td align="center"><a href="docs/validation.md">Validation</a></td></tr>
<tr><td align="center"><strong>Export & Packaging</strong></td><td align="left">Export to an explicit destination, copy resolved assets, and rewrite references without changing the source.</td><td align="left">Model + assets → URDF / MJCF / JSON / portable package</td><td align="center">Beta</td><td align="center"><a href="docs/export.md">Export</a></td></tr>
<tr><td align="center"><strong>Workspaces</strong></td><td align="left">Save source references, committed edits, poses, and interface settings.</td><td align="left">Session state → workspace YAML</td><td align="center">Beta</td><td align="center"><a href="docs/workspaces.md">Workspaces</a></td></tr>
<tr><td align="center"><strong>Desktop Application</strong></td><td align="left">Run the local API and editor inside a native Windows pywebview window.</td><td align="left">Packaged app → Windows desktop editor</td><td align="center">Beta</td><td align="center"><a href="docs/desktop_build.md">Desktop build</a></td></tr>
</tbody></table>

<a id="formats"></a>
<h2 align="center">Supported formats</h2>

<table align="center"><thead><tr><th align="center">Format</th><th align="center">Import</th><th align="center">Export</th><th align="center">Support</th><th align="left">Notes</th></tr></thead><tbody>
<tr><td align="center">URDF</td><td align="center">Yes</td><td align="center">Yes</td><td align="center">Supported</td><td align="left">Core robot model format</td></tr>
<tr><td align="center">Xacro</td><td align="center">Yes</td><td align="center">Expanded URDF</td><td align="center">Partial</td><td align="left">Explicit package maps work without ROS</td></tr>
<tr><td align="center">MJCF</td><td align="center">Yes</td><td align="center">Yes</td><td align="center">Partial</td><td align="left">Static structural conversion; review output fidelity</td></tr>
<tr><td align="center">STEP</td><td align="center">Adapter required</td><td align="center">No</td><td align="center">Experimental</td><td align="left">Requires a separately installed step2urdf adapter</td></tr>
<tr><td align="center">USD</td><td align="center">No</td><td align="center">No</td><td align="center">Planned</td><td align="left">Requires a verified Isaac Sim integration</td></tr>
</tbody></table>

<a id="requirements"></a>
<h2 align="center">Requirements and verified environments</h2>

<table align="center"><thead><tr><th align="center">Component</th><th align="center">Supported range</th><th align="left">Currently verified</th></tr></thead><tbody>
<tr><td align="center">Python</td><td align="center">3.9–3.13</td><td align="left">CI: 3.9, 3.11, and 3.13</td></tr>
<tr><td align="center">Node.js</td><td align="center">20–24</td><td align="left">CI: Node.js 22</td></tr>
<tr><td align="center">pnpm</td><td align="center">10–11</td><td align="left">CI: pnpm 11</td></tr>
<tr><td align="center">Desktop</td><td align="center">Windows</td><td align="left">Windows pywebview and PyInstaller workflow</td></tr>
<tr><td align="center">Browser development</td><td align="center">Windows / Linux</td><td align="left">Playwright Chromium E2E on Ubuntu</td></tr>
</tbody></table>

<a id="quick-start"></a>
<h2 align="center">Quick start from source</h2>

Morphology Studio is currently distributed as an alpha source release; a prebuilt installer is not yet published. The setup script installs the desktop and documentation extras, locked frontend dependencies, and the Playwright browser.

```powershell
git clone https://github.com/sichenglil/Morphology_Studio.git
Set-Location Morphology_Studio
python -m venv .venv
.\.venv\Scripts\Activate.ps1
./scripts/setup_dev.ps1
python desktop_entry.py
```

Open `assets/robot_models/ur5e_hx5_right/robot.urdf`. Browser development uses `./scripts/run_web.ps1` plus `pnpm --dir web/frontend dev` in a second terminal.

Run the complete local verification suite with `./scripts/test_all.ps1`.

<a id="five-minute-workflow"></a>
<h2 align="center">Five-minute workflow</h2>

1. Select **Import model** and open the generic two-link example.
2. Select `arm` in the model tree; orbit and focus the 3D viewport.
3. Move the joint slider or type an exact value and press Enter.
4. Use `W` and `E` to switch the transform gizmo between move and rotate.
5. Import `assets/robot_models/ur5e_hx5_right/robot.urdf`, open **Assembly**, and create a fixed joint.
6. Run **Validation**, choose an output destination, and export a portable package.

<a id="gallery"></a>
<h2 align="center">Screenshot gallery</h2>



<a id="architecture"></a>
<h2 align="center">Architecture</h2>

The Vue/Three.js editor talks to a local FastAPI service. Importers populate one in-memory `RobotModel`; validators, workspaces, and exporters consume that same model, while pywebview supplies only the native window and controlled file selection. See [architecture.md](docs/architecture.md).

<a id="repository-structure"></a>
<h2 align="center">Repository structure</h2>

| Path | Purpose |
|:--:|:--:|
| `.github/` | CI, release automation, issue and pull-request templates |
| `packaging/windows/` | PyInstaller Windows packaging configuration |
| `src/morphology_toolkit/` | Robot-agnostic Python backend and packaged frontend assets |
| `web/frontend/` | Sole editable Vue 3 and Three.js frontend |
| `tests/` | Python unit, integration, documentation, and local acceptance tests |
| `assets/robot_models/ur5e_hx5_right/` | Packaged combined robot model |
| `docs/` | User, architecture, maintainer, audit, and visual documentation |
| `scripts/` | Stable entry scripts plus grouped development and migration helpers |
| `configs/` | Optional package maps and acceptance configuration |

Generated output belongs in ignored `build/`, `dist/`, `generated/`, or a user workspace. See [repository_structure.md](docs/repository_structure.md).

<a id="roadmap"></a>
<h2 align="center">Roadmap</h2>

- **Stable:** strengthen URDF resource diagnostics and large-model regression coverage.
- **Beta:** improve Xacro/MJCF fidelity, assembly ergonomics, and workspace migration.
- **Planned:** optional ROS 2 and Isaac adapters when verified environments are available.

<h2 align="center">Contributing, security, and license</h2>

Read [CONTRIBUTING.md](CONTRIBUTING.md), report vulnerabilities privately through [SECURITY.md](SECURITY.md), and use the provided issue templates without attaching proprietary models. Morphology Studio is licensed under [Apache-2.0](LICENSE); dependency attribution is recorded in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

