# Morphology Studio

面向 URDF、Xacro 与 MJCF 的通用机器人模型导入、三维检查、装配、验证和转换工具。Python
`RobotModel` 是唯一事实来源；UR5e 与 HX5 仅用于示例和本地验收。

## Windows 开发环境

```powershell
python -m pip install -e ".[dev,desktop]"
pnpm --dir web/frontend install
pnpm --dir web/frontend build
```

启动原生桌面窗口：

```powershell
python desktop_entry.py
# 或
morphology-tool desktop
```

如果本机缺少 WebView2，可显式使用浏览器回退：

```powershell
morphology-tool desktop --browser
```

## 基本工作流

1. 点击“导入模型”，选择 URDF、Xacro 或模型目录；目录候选与低置信度推断会要求确认。
2. 在左侧模型树选择 Link/Joint，并在中央 Three.js 视口检查真实网格。
3. 使用底部关节滑块检查通用正向运动学；右侧 Inspector 显示变换、轴向、限位和几何信息。
4. 使用“装配”选择父 Link、子模型根 Link 和 XYZ/RPY，创建通用 fixed 连接。
5. 运行验证并从“导出”生成 URDF、MJCF、Morphology JSON 或可移植资源包。

源模型不会被界面修改；生成内容写入用户工作区、`build/` 或 `generated/`。

## 无 ROS 的 Xacro

```powershell
morphology-tool build-xacro --input model.urdf.xacro --output build/model.urdf --package-map configs/package_maps/local_models.yaml
```

本机没有 ROS 2、Isaac Sim 或 Isaac Lab。相关状态严格显示为 `NOT_AVAILABLE_LOCAL`，不会生成
伪造 USD 或远程验收结果。

## 测试

```powershell
$env:PYTHONPATH = "$PWD\src"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -q
python -m ruff check src tests
pnpm --dir web/frontend type-check
pnpm --dir web/frontend lint
pnpm --dir web/frontend test
pnpm --dir web/frontend build
```

## 构建 EXE

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_desktop.ps1
powershell -ExecutionPolicy Bypass -File scripts/smoke_test_desktop.ps1
dist\MorphologyStudio\MorphologyStudio.exe
```

发布单元是整个 `dist\MorphologyStudio` 目录。日志位于
`%LOCALAPPDATA%\MorphologyStudio\logs\morphology-studio.log`。更多信息见
[桌面架构](docs/desktop_architecture.md)、[故障排查](docs/desktop_troubleshooting.md)和
[界面验收报告](docs/ui_acceptance_report.md)。
