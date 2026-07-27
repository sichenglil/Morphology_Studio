# 模型装配

装配配置可声明任意模型、前缀和多个连接。第一版实际执行 fixed joint：

```powershell
python -m morphology_toolkit assemble --config configs/examples/ur5e_hx5_right_assembly.yaml --mode assisted --output build/real_models/ur5e_hx5_right/ur5e_hx5_right.urdf
```

示例安装位姿为零位，仅用于结构测试，标记为 `TEST_MOUNT_TRANSFORM_NOT_PHYSICALLY_CALIBRATED`。不得把它视为正式机械安装尺寸。

