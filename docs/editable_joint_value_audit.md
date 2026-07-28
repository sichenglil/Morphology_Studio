# Editable joint value audit

The former read-only value was the `<b>{{ value.toFixed(3) }}</b>` node in `JointSlider.vue`. Its value came from the Pinia `jointValues` map. Slider `input` called `previewJoint`, which updates the indexed Three.js joint motion object through `jointRuntimeBridge`; slider `change` called the 80 ms batched backend commit.

Joint limits come from each `JointNode.limit` parsed from URDF. Internal rotational values are radians and prismatic values are metres. Runtime preview does not parse URDF, rebuild the scene, reload meshes, or fetch the scene API. The replacement `JointValueInput.vue` preserves draft text independently from parsed and committed values and reuses that pipeline.
