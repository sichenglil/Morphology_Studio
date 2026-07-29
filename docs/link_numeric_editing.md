# Precise Link transform editing

Select a Link and expand **Transform** in the right inspector. For a non-root Link the panel names the parent Joint and edits that Joint's URDF `<origin>`; Links do not own a kinematic origin. A root Link edits the workspace model-instance transform. Joint, assembly connection, Visual, and Collision selections map to their corresponding origin fields through the backend transform resolver.

XYZ is stored in metres and can be displayed in m, cm, or mm. RPY is stored in radians and can be displayed in degrees or radians. Quaternion X/Y/Z/W is normalized before conversion to RPY; zero-length and non-finite values are rejected. Editing changes only a local Three.js preview. **Apply** sends one revision-checked commit and creates one history item; **Cancel** restores the original preview. Copy/paste uses a structured `morphology-transform` JSON payload.

Workspace YAML stores transform history and editor settings. Reopening replays committed edits. URDF export serializes the edited Joint, Visual, or Collision origin.
