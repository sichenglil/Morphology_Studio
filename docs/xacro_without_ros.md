# 无 ROS 展开 Xacro

工具优先调用 Python `xacro.process_file()`，并在当前调用范围内替换 `xacro.substitution_args._eval_find`。替换结果只来自 `PackageResolver`；执行结束后立即恢复原函数，不安装伪 ROS 模块，也不修改源 Xacro。

支持：Xacro 宏、参数、include、`$(find package)`、package map、含空格的 Windows 路径。未知 substitution、缺包、残留 `${...}` 或 `<xacro:...>` 会明确失败。

不支持：依赖运行中 ROS graph、ament 插件或外部 ROS 节点的表达式。

