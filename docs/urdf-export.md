# URDF and portable export

Morphology Studio exports UTF-8 XML with escaped names/attributes, forward-slash resource URIs,
visual and collision geometry, inertial data, fixed/revolute/continuous/prismatic joints, axes,
limits, damping and friction. Run model validation before export; `check_urdf` remains an optional
external verification when ROS tooling is available.

The portable directory contains `robot.urdf`, copied content-addressed resources, `manifest.json`,
`validation.json` and `validation.md`. Portable ZIP produces the same directory as one archive and
does not modify source models. Absolute resource paths are validation errors.
