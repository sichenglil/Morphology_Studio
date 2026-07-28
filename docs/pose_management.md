# Pose management

`保存姿态` stores all scalar movable joint values under a user-provided name in local application storage. Select a saved pose and choose `加载` to preview all joints and send one batch backend commit. `全部归零` uses the same batch path. Fixed, planar, and floating joints are excluded.

Workspace serialization continues to store committed joint state separately from URDF joint origins. Pose presets do not modify source model files.
