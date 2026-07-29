# Package map

Package map 将 ROS 包名映射到本地目录，路径相对项目根目录：

```yaml
packages:
  example_description:
    path: models/example_description
```

诊断命令：

```powershell
python -m morphology_toolkit inspect-package-map --package-map config/models/package_maps/local_models.yaml
```

优先级为显式映射、用户 package roots、目录扫描。Assisted 模式遇到重复包名会拒绝静默选择，并返回搜索轨迹。
