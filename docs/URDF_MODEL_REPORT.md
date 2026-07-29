# URDF model migration report

## Source and selection

The only selected package is `processed_models/portable_packages/ur5e_hx5_right`. The source directory was treated as read-only. A self-contained copy is stored at `assets/robot_models/ur5e_hx5_right`.

The package contains one merged `robot.urdf`, 40 links, 39 joints and 56 mesh references. All referenced DAE/STL files resolve through relative paths; no mesh is missing and no ROS package URI is needed.

## Preview

`scripts/generate_urdf_gifs.py` parses the URDF transforms and real meshes, normalizes the camera to the model bounds, and renders a 512 x 512, 60-frame, 20 FPS turntable. Outputs are `assets/previews/ur5e_hx5_right/robot.gif` and `robot.png`. A content digest cache avoids unnecessary regeneration.

Original package manifests containing development-machine source paths were moved to `_archive/model_package_metadata`; they are not runtime dependencies or release assets.
