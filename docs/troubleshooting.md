# 故障排查

## pytest 卡在 collecting

本机存在无关全局插件冲突：

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -q
```

## Package not found

检查 `configs/package_maps/local_models.yaml`，再运行 `inspect-package-map`。不要把绝对 `G:\` 路径写进 YAML。

## Xacro 不可用

```powershell
python -m pip install xacro
```

## USD 转换失败

本机没有 Isaac Sim，预期结果为 `NOT_AVAILABLE_LOCAL`。CLI 会返回非零退出码，不会创建假 USD。

