# Reference alignment matrix

| Reference capability | Morphology Studio component | Previous state | This phase | Local acceptance |
|---|---|---|---|---|
| Central 3D viewport | `RobotViewport.vue` | Missing | Required | render and interaction test + screenshot |
| Model hierarchy | `ModelTree.vue` | JSON only | Required | expand/select test |
| Context inspector | `RightInspector.vue` | Missing | Required | editable-field test |
| Joint controls | `JointControlPanel.vue` | Missing | Required | slider/FK state test |
| Visual assembly | `AssemblyWizard.vue` | CLI only | Required | generic fixed-connection test |
| Import workflow | `ImportWizard.vue` | basic API | Required | real URDF/Xacro examples |
| Validation | `ValidationPanel.vue` | backend only | Required | issue navigation test |
| Export | `ExportDialog.vue` | backend only | Required | URDF/MJCF local export |
| Native window | pywebview host | browser launcher | Required | windowed EXE smoke test |
| Safe logging | `logging_config.py` | unsafe Uvicorn default | Required | stdout/stderr `None` tests |
| Source of truth | Python `RobotModel` APIs | Present | Preserve | backend regression suite |

The target is structural and workflow alignment with an original visual design. It is not a visual
clone of either reference product.
