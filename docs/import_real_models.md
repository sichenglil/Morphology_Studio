# 导入真实模型

先扫描候选，再使用示例配置生成：

```powershell
python -m morphology_toolkit import --path models/ur_description --package-map configs/package_maps/local_models.yaml --mode assisted
python scripts/build_xacro_model.py --config configs/examples/ur5e_local.yaml --output build/real_models/ur5e/ur5e.urdf --trace build/reports/ur5e_generation_trace.json --validation-json build/reports/ur5e_validation.json --validation-md build/reports/ur5e_validation.md
python scripts/build_xacro_model.py --config configs/examples/hx5_d20_rev2_right.yaml --output build/real_models/hx5_d20_rev2_right/hx5_d20_rev2_right.urdf --trace build/reports/hx5_generation_trace.json --validation-json build/reports/hx5_validation.json --validation-md build/reports/hx5_validation.md
```

SRDF 会显示为语义文件，但不会成为几何入口。生成器不会写入 `models/`。

