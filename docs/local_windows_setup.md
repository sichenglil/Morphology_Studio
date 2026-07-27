# Windows 本地安装

要求 Python 3.9+。执行：

```powershell
python -m pip install -e ".[dev,web,mesh]"
python -m pip install xacro
$env:PYTHONPATH = "$PWD\src"
```

本机没有 ROS 2、Isaac Sim 和 Isaac Lab；这些状态在环境报告中标为 `NOT_AVAILABLE_LOCAL`。所有源模型只读，输出位于 `build/`、`generated/` 或 `workspace/`。

