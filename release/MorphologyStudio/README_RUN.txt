Morphology Studio 0.1.0

双击 MorphologyStudio.exe 启动。
请勿单独移动 EXE；_internal、assets 和 config 必须与 EXE 一起复制。
EXE 已内置 OpenCascade WebAssembly，可直接选择 STEP/STP，无需安装 step2urdf、Node.js 或 pnpm。
首次解析 STEP 会加载约 50 MB 的本地 WASM，属于正常现象，不需要联网。
生成的 STEP 网格缓存位于 %LOCALAPPDATA%\MorphologyStudio\step_imports。
日志位于 logs\MorphologyStudio.log。
第三方许可证位于 _internal\licenses。
Windows 需要 Microsoft Edge WebView2 Runtime。
