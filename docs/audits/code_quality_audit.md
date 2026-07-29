# Code quality audit

The in-memory `RobotModel` separates import, resources, assembly, validation, workspace, and export responsibilities. The main API module is comparatively large and should be split by router in a future compatibility-preserving change. Existing desktop stream handling, revision checks, incremental joint runtime, render scheduling, and Three.js resource cache are regression-sensitive and were retained.

Risk checks cover malformed numeric transforms, stale revisions, path resolution, XML fidelity, desktop shutdown, and source-read-only behavior. Core code contains no fixed robot/link names. Machine-location probing is limited to optional Isaac availability reports; it does not claim validation. The frontend's generated bundle is not linted as source.
