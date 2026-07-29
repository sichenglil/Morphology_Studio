# 可移植资源包

```powershell
python -m morphology_toolkit package --input build/real_models/ur5e/ur5e.urdf --output build/packages/ur5e --package-map configs/package_maps/local_models.yaml
```

输出包含 `robot.urdf`、`meshes/`、`textures/`、`resources/`、SHA-256 `manifest.json` 和验证报告。URDF 中资源会改为相对路径；包可以脱离原模型目录重新导入。

