# Joint runtime architecture

The reactive layer owns IDs, numeric joint values and UI state. Three.js objects stay in component-local,
plain TypeScript runtime structures and never enter Pinia or Vue deep proxies.

```text
Robot root
└── Link
    └── Joint origin (static URDF xyz/rpy)
        └── Joint motion (dynamic axis/value)
            └── Child Link
```

`RobotRuntimeIndex` maps stable Link, Joint, Visual and Collision IDs. `JointController` clamps values and
changes only the indexed motion object. Revolute/continuous joints set an axis-angle quaternion; prismatic
joints set axis-scaled position; fixed joints reject live values. `RenderScheduler` has a Set of continuous
reasons, coalesces invalidations and returns to zero idle RAF work when interaction stops.
