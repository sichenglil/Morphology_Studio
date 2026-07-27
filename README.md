# Morphology Toolkit

通用机器人模型导入、装配、验证、资源打包和转换工具。核心代码不依赖具体机器人；仓库中的 UR 与 ROBOTIS 模型仅用于本地验收。

## Windows 快速开始

```powershell
Set-Location "G:\Code_Programs\VscodeProjects\Robot\Morphology-Conditioned"
python -m pip install -e ".[dev]"
$env:PYTHONPATH = "$PWD\src"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -q
```

本机无需 ROS 2。Python `xacro` 配合 [package map](configs/package_maps/local_models.yaml) 可以展开使用 `$(find package)` 的模型。

## 常用命令

```powershell
python -m morphology_toolkit audit
python -m morphology_toolkit import --path models/ur_description --package-map configs/package_maps/local_models.yaml --mode assisted
python -m morphology_toolkit inspect-package-map --package-map configs/package_maps/local_models.yaml
python -m morphology_toolkit assemble --config configs/examples/ur5e_hx5_right_assembly.yaml --output build/real_models/combined/robot.urdf
python -m morphology_toolkit validate --input build/real_models/ur5e/ur5e.urdf --package-map configs/package_maps/local_models.yaml
python -m morphology_toolkit package --input build/real_models/ur5e/ur5e.urdf --output build/packages/ur5e --package-map configs/package_maps/local_models.yaml
python -m morphology_toolkit convert --input build/packages/ur5e/robot.urdf --format mjcf --output build/mjcf/ur5e.xml
python -m morphology_toolkit web
```

## 真实模型生成

```powershell
python scripts/build_xacro_model.py --config configs/examples/ur5e_local.yaml --output build/real_models/ur5e/ur5e.urdf --trace build/reports/ur5e_generation_trace.json --validation-json build/reports/ur5e_validation.json --validation-md build/reports/ur5e_validation.md
python scripts/build_xacro_model.py --config configs/examples/hx5_d20_rev2_right.yaml --output build/real_models/hx5_d20_rev2_right/hx5_d20_rev2_right.urdf --trace build/reports/hx5_generation_trace.json --validation-json build/reports/hx5_validation.json --validation-md build/reports/hx5_validation.md
```

## 本机能力边界

- URDF、无 ROS Xacro、装配、验证、打包、MJCF 静态转换：本机已测试。
- Isaac Sim USD、Isaac Lab、ROS 2 原生索引：`NOT_AVAILABLE_LOCAL`，不会生成假输出。
- Web 当前是基础扫描/结构接口，不是完整 Three.js 编辑器。

详细说明见 [docs/local_windows_setup.md](docs/local_windows_setup.md) 和 [docs/troubleshooting.md](docs/troubleshooting.md)。第三方信息见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

