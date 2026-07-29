# MJCF 转换

```powershell
python -m morphology_toolkit convert --input build/packages/ur5e/robot.urdf --format mjcf --output build/mjcf/ur5e.xml
python scripts/dev/validate_mjcf.py --input build/mjcf/ur5e.xml --json build/reports/ur5e_mjcf_conversion.json --markdown build/reports/ur5e_mjcf_conversion.md
```

转换器生成 body 树、joint/axis/range、inertial、mesh asset 和 visual geom。本机没有 MuJoCo runtime，因此运行时状态为 `MUJOCO_RUNTIME_NOT_INSTALLED`；XML 与资源静态检查已执行。
