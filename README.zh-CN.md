<div align="center">

# Morphology Studio

<p>面向机器人模型检查、编辑、装配、验证与转换的源文件保护型桌面工作区。</p>

<p><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a></p>

<p>
  <a href="https://github.com/sichenglil/Morphology_Studio/actions/workflows/backend-ci.yml"><img alt="后端 CI" src="https://github.com/sichenglil/Morphology_Studio/actions/workflows/backend-ci.yml/badge.svg"></a>
  <a href="https://github.com/sichenglil/Morphology_Studio/actions/workflows/frontend-ci.yml"><img alt="前端 CI" src="https://github.com/sichenglil/Morphology_Studio/actions/workflows/frontend-ci.yml/badge.svg"></a>
  <a href="https://github.com/sichenglil/Morphology_Studio/actions/workflows/e2e.yml"><img alt="端到端测试" src="https://github.com/sichenglil/Morphology_Studio/actions/workflows/e2e.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue.svg"></a>
</p>

<p><strong>版本 0.1.1 · Alpha · 核心功能无需 ROS · ROS 2 与 Isaac 集成规划中</strong></p>

<p><a href="#demo">演示</a> · <a href="#download">下载</a></p>

</div>

<a id="demo"></a>
## 软件内机械臂操作演示

以下动画是在 Morphology Studio 中实际加载 `ur5e_hx5_right`，并操作机械臂关节时录制生成的。

<p align="center"><img src="assets/previews/ur5e_hx5_right/robot.gif" width="960" alt="在 Morphology Studio 中操作 UR5e 与 HX5 Right 组合机械臂"></p>

- GIF 来自真实软件界面，展示模型加载及机械臂关节操作过程。
- 最终应用和 EXE 使用 `assets/robot_models/ur5e_hx5_right` 中的项目内部副本。
- 运行程序不需要原始 Morphology-Conditioned 项目。
- 使用 `python scripts/render/generate_software_demo_gif.py` 可重新录制。

## UR5e 与灵巧手装配过程

以下动画记录真实的软件操作流程：导入独立 UR5e 模型，在装配窗口选择独立
HX5 灵巧手作为子模型，将灵巧手根节点连接到 UR5e 的 `tool0`，并显示最终的
40-Link 组合机器人，最后将装配结果导出。动画中的本地模型路径和导出路径
均已模糊处理，避免暴露个人目录信息。

<p align="center"><img src="assets/previews/ur5e_hx5_right/assembly_workflow.gif" width="960" alt="在 Morphology Studio 中分别导入并装配 UR5e 与 HX5 灵巧手"></p>

使用 `python scripts/render/generate_assembly_demo_gif.py` 可重新录制。

<a id="download"></a>
## 下载

各平台安装包均在对应操作系统的原生 GitHub Runner 上构建。正式版本请访问
[GitHub Releases](https://github.com/sichenglil/Morphology_Studio/releases)，开发构建可从最近一次成功的
[跨平台构建任务](https://github.com/sichenglil/Morphology_Studio/actions/workflows/build-release.yml)下载。

| 操作系统 | 架构 | 下载文件 | 运行说明 |
|:--|:--:|:--|:--|
| Windows 10/11 | x64 | [`MorphologyStudio-0.1.0-windows-x64.exe`](https://github.com/sichenglil/Morphology_Studio/releases/latest/download/MorphologyStudio-0.1.0-windows-x64.exe) | 需要 Microsoft Edge WebView2 Runtime |
| Linux | x86_64 | [`MorphologyStudio-0.1.0-linux-x86_64.tar.gz`](https://github.com/sichenglil/Morphology_Studio/releases/latest/download/MorphologyStudio-0.1.0-linux-x86_64.tar.gz) | 需要 GTK 3 和 WebKitGTK 4.1 |
| macOS | Apple Silicon | [`MorphologyStudio-0.1.0-macos-arm64-unsigned.zip`](https://github.com/sichenglil/Morphology_Studio/releases/latest/download/MorphologyStudio-0.1.0-macos-arm64-unsigned.zip) | 原生 arm64，当前未签名 |
| macOS | Intel | [`MorphologyStudio-0.1.0-macos-x64-unsigned.zip`](https://github.com/sichenglil/Morphology_Studio/releases/latest/download/MorphologyStudio-0.1.0-macos-x64-unsigned.zip) | 原生 x86_64，当前未签名 |

> `v0.1.0` 已正式发布，上方直接下载链接均已生效。每个正式版本同时提供
> `SHA256SUMS.txt`，开发构建仍可从 Actions 下载。安装方法参见
> [跨平台安装与打包说明](docs/cross-platform-packaging.md)。

## 打包内容与最小可执行单元

| 平台安装包 | 内置内容 | 最小可执行单元 | 必须一起保留的文件 |
|:--|:--|:--|:--|
| Windows `.exe` | Python 运行时、后端、编译后前端、OpenCascade WASM/Worker、配置、许可证和示例资源 | **单个 `MorphologyStudio-0.1.0-windows-x64.exe` 文件** | 无需携带其他项目文件；WebView2 属于 Windows 系统运行时依赖 |
| Linux `.tar.gz` | `MorphologyStudio/` 主程序及其 Python 库、前端、WASM/Worker、配置、许可证和资源 | **完整解压后的 `MorphologyStudio/` 文件夹** | 不能只复制 `MorphologyStudio/MorphologyStudio`；旁边的 `_internal/` 必须保留 |
| macOS `.zip` | 原生 `.app` Bundle，包含主程序、Python 库、前端、WASM/Worker、配置、许可证和资源 | **完整的 `MorphologyStudio.app` 应用包** | 不能只提取或复制 `Contents/MacOS/MorphologyStudio` |

压缩包是下载和传输单元，不一定是运行单元。Windows 版本是真正的单文件；Linux 为减少每次启动
解压耗时采用优化后的 onedir 结构，整个目录都是最小运行单元；macOS 的 `.app` 在 Finder 中看似
单个应用，实际是不可拆分的目录 Bundle。用户模型、导出的 URDF 和日志属于外部数据，程序启动时
不要求预先携带这些文件。

<a id="overview"></a>
## 项目概览

Morphology Studio 在保持源模型只读的前提下，为检查和准备机器人模型提供统一工作区。核心逻辑不绑定机器人名称、连杆名称、关节数量或固定目录，模型结构均在导入时自动解析。

| 保护源文件 | 与机器人型号无关 | 无需 ROS 的工作流 |
|:--|:--|:--|
| 编辑记录和生成文件始终与原始模型分离。 | 从输入数据自动识别结构、名称和资源。 | 通过显式 package map 展开 Xacro 并生成可移植包。 |

<a id="features"></a>
## 功能模块

下表说明每个模块解决的问题、主要操作、输入输出、成熟度及详细文档。

| 模块 | 用途与操作 | 输入 → 输出 | 状态 | 文档 |
|:--:|:--|:--|:--:|:--:|
| **模型导入** | 打开文件或扫描目录；低置信度选择需要用户确认。 | URDF / Xacro / MJCF / 目录 → 规范化机器人模型 | 稳定 / 部分格式测试中 | [导入](docs/import_models.md) |
| **模型树与三维视口** | 搜索大型层级，并在 Three.js 场景中检查基础几何与已解析的 STL/DAE 网格。 | 模型 + 资源 → 同步的模型树与三维选择 | 稳定 | [用户指南](docs/user_guide.md) |
| **关节控制** | 通过滑块或精确数值预览运动，支持单位、精度和限位反馈。 | 关节限位 + 数值 → 机器人姿态 | 稳定 | [关节控制](docs/joint_control.md) |
| **变换编辑** | 通过操作柄或 XYZ/RPY 精确字段移动、旋转对象。 | 对象 + 变换 → 可追踪的模型修改 | 测试中 | [变换](docs/transform_editing.md) |
| **模型装配** | 选择父子根节点，创建通用 fixed 连接。 | 两个模型 + 位姿 → 组合模型 | 测试中 | [装配](docs/assembly.md) |
| **验证** | 检查名称、拓扑、限位、资源和导出就绪状态。 | 当前模型 → 可处理的错误和警告 | 测试中 | [验证](docs/validation.md) |
| **导出与资源打包** | 导出到明确位置，复制已解析资源并改写引用，全程不修改源文件。 | 模型 + 资源 → URDF / MJCF / JSON / 可移植包 | 测试中 | [导出](docs/export.md) |
| **工作区** | 保存源引用、已提交修改、姿态和界面设置。 | 会话状态 → workspace YAML | 测试中 | [工作区](docs/workspaces.md) |
| **桌面应用** | 通过各系统原生 pywebview 窗口运行本地 API 和编辑器。 | 发行包 → Windows、Linux 或 macOS 桌面编辑器 | 测试中 | [桌面构建](docs/cross-platform-packaging.md) |

<a id="formats"></a>
## 支持格式

| 格式 | 导入 | 导出 | 支持状态 | 说明 |
|:--:|:--:|:--:|:--:|:--|
| URDF | 是 | 是 | 已支持 | 核心机器人模型格式 |
| Xacro | 是 | 展开为 URDF | 部分支持 | 显式 package map 可在无 ROS 环境使用 |
| MJCF | 是 | 是 | 部分支持 | 静态结构转换，建议检查输出保真度 |
| STEP | 是（内置辅助模式） | URDF / 可移植包 | 实验性 | 桌面应用内置 OpenCascade WASM，离线直接解析 |
| USD | 否 | 否 | 规划中 | 需要经过验证的 Isaac Sim 集成 |

<a id="requirements"></a>
## 运行要求与验证环境

| 组件 | 支持范围 | 当前验证环境 |
|:--:|:--:|:--|
| Python | 3.9–3.13 | CI：3.9、3.11、3.13 |
| Node.js | 20–24 | CI：Node.js 22 |
| pnpm | 10–11 | CI：pnpm 11 |
| 桌面应用 | Windows / Linux / macOS | 原生 PyInstaller 构建矩阵：WebView2、GTK/WebKitGTK、WKWebView |
| 浏览器开发 | Windows / Linux | Ubuntu 上的 Playwright Chromium 端到端测试 |

<a id="quick-start"></a>
## 从源码快速开始

Morphology Studio 当前为 Alpha 版本。普通用户可使用下载表中的 CI 构建包；源码开发可按下列步骤安装。安装脚本会安装桌面与文档依赖、锁定的前端依赖和 Playwright 浏览器。

```powershell
git clone https://github.com/sichenglil/Morphology_Studio.git
Set-Location Morphology_Studio
python -m venv .venv
.\.venv\Scripts\Activate.ps1
./scripts/maintenance/setup_dev.ps1
python project/desktop_entry.py
```

首次导入 `assets/robot_models/ur5e_hx5_right/robot.urdf`。浏览器开发模式运行 `./scripts/maintenance/run_web.ps1`，并在第二个终端运行 `pnpm --dir web/frontend dev`。

使用 `./scripts/validation/test_all.ps1` 运行完整本地验收。

## 直接导入 STEP

在桌面应用的“导入模型”中直接选择 `.step` 或 `.stp`。内置 OpenCascade WebAssembly Worker
会离线解析并三角化实体；随后在同一向导中确认 Link 名称、父实体、关节类型和关节轴，点击
“导入并显示”即可进入三维工作区。运行 EXE 不需要另行安装 step2urdf、Node.js 或 pnpm。

STEP 几何不包含可靠的机器人运动语义，因此程序不会静默猜测完整机构。实体可自动成为 Link
候选，但父子关系、fixed/revolute/continuous/prismatic 类型及运动轴需要人工确认。内置 WASM
未压缩约 50 MB，大型 CAD 装配仍受 WebView2 可用内存限制。

<a id="five-minute-workflow"></a>
## 五分钟使用流程

1. 点击“导入模型”，打开通用两连杆示例。
2. 在模型树选择 `arm`，旋转视口并聚焦对象。
3. 拖动关节滑块，或输入精确值并按 Enter。
4. 使用 `W`/`E` 切换移动和旋转操作柄。
5. 导入 `assets/robot_models/ur5e_hx5_right/robot.urdf`，通过“装配”创建 fixed 连接。
6. 运行“验证”，选择输出位置并导出可移植资源包。

<a id="architecture"></a>
## 架构

Vue/Three.js 编辑器通过本地 HTTP 调用 FastAPI。导入器写入唯一的内存 `RobotModel`，验证、工作区和导出器共享该模型；pywebview 仅提供原生窗口和受控文件选择。详见 [architecture.md](docs/architecture.md)。

<a id="repository-structure"></a>
## 项目结构

| 路径 | 用途 |
|:--:|:--|
| `.github/` | CI、发布流程、Issue 与 PR 模板 |
| `scripts/build/packaging/` | Windows PyInstaller 打包配置 |
| `src/morphology_toolkit/` | 通用 Python 后端和发行版前端资源 |
| `web/frontend/` | 唯一可编辑 Vue 3 / Three.js 前端 |
| `tests/` | Python 单元、集成、文档和本地验收测试 |
| `assets/robot_models/ur5e_hx5_right/` | 内置组合机械臂模型 |
| `docs/` | 用户、架构、维护、审计和视觉文档 |
| `scripts/` | 稳定入口以及分组后的开发和迁移工具 |
| `config/` | 应用、模型清单与 package map 配置 |

生成内容只能进入已忽略的 `build/`、`dist/`、`generated/` 或用户工作区。详细结构见 [repository_structure.md](docs/repository_structure.md)。

<a id="roadmap"></a>
## 路线图

- **Stable：**加强 URDF 资源诊断和大型模型回归测试。
- **Beta：**提升 Xacro/MJCF 保真度、装配体验和工作区迁移。
- **Planned：**在具备可验证环境后增加可选 ROS 2 与 Isaac 适配器。

## 贡献、安全与许可证

贡献前阅读 [CONTRIBUTING.md](docs/governance/CONTRIBUTING.md)，漏洞按 [SECURITY.md](docs/governance/SECURITY.md) 私下报告，提交 Issue 时不要附带专有模型。本项目采用 [Apache-2.0](LICENSE)，依赖与致谢见 [THIRD_PARTY_NOTICES.md](project/THIRD_PARTY_NOTICES.md)。
