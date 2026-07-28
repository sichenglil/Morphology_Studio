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

### 鼠标变换编辑

视口单击可选择零件；选中项使用青色包围框和原生 Three.js `TransformControls` 操作柄。默认是
“装配编辑”，内部 Link 被锁定，只允许移动整机根实例、装配连接以及 Visual/Collision；切换到
“运动学编辑”后，移动非根 Link 会写回其父 Joint 的 `origin`。缩放仅适用于 Visual/Collision。

- `Q` 清除选择，`W/E/R` 移动/旋转/缩放，`X` 切换局部/世界坐标。
- `F` 或 `Home` 聚焦模型，`Esc` 取消选择，`Ctrl+Z` 撤销，`Ctrl+Y` 或 `Ctrl+Shift+Z` 重做。
- 可开启平移、5° 旋转和缩放吸附；输入框获得焦点时不会触发快捷键。
- 拖动只在浏览器内实时预览，松开鼠标后提交一次。服务端通过 workspace revision 拒绝过期提交，
  并拒绝 `NaN`/`Infinity`。数值 Inspector 与视口共享同一提交和历史链路。

工作区可保存为 `workspace.yaml`，记录源模型、根变换、已提交编辑与界面设置；重新打开时会从只读
源模型重建并重放编辑。导出 URDF 时 Joint/Visual/Collision 的变换与几何缩放来自同一内存模型。

关节滑块使用本地增量 FK：拖动实时更新 Joint Motion，同一帧事件合并渲染，松手后才批量提交。
使用 `?debugPerformance=1` 打开 FPS、FK、Render、Draw Calls、Triangles、重建及网格加载诊断面板。
详见 [渲染性能](docs/rendering_performance.md) 与 [运行时架构](docs/joint_runtime_architecture.md)。

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
