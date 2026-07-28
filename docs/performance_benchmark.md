# Joint rendering benchmark

Local production build, Microsoft Edge through Playwright at 1440×900. The browser exposed a 120 Hz RAF
cadence; FPS is reported as observed data, while regression tests enforce architecture counters.

| Model | updates | FPS | frame ms | average FK/update ms | P95 update ms | draw calls | triangles |
|---|---:|---:|---:|---:|---:|---:|---:|
| two-link runtime | 1000 | n/a | n/a | 0.0028 | 0.0058 | n/a | n/a |
| UR5e | 120 | 120.41 | 9.30 | 0.1283 | 0.30 | 33 | 121,789 |
| HX5-D20 Rev2 Right | 120 | 120.35 | 8.82 | 0.0758 | 0.20 | 28 | 236,060 |
| UR5e + HX5 | 120 | 120.26 | 8.61 | 0.1367 | 0.30 | 59 | 357,849 |

For every real model, runtime construction occurred once, resource loads equaled initial unique visuals,
120 previews caused zero backend requests, workspace saves and full validations, and mouse release caused
one batch commit. The two-link 1000-update burst scheduled one RAF and caused zero rebuilds or mesh loads.

The pre build had no timing instrumentation, so its timing fields remain explicitly null. Its call chain was
reproduced and gives exact architectural counts per 1000 inputs: 1000 PATCH requests, 1000 deep-watch scene
rebuilds and 1000 full mesh-loader passes. This report does not invent a before FPS value.

Run:

```powershell
pnpm --dir web/frontend test
pnpm --dir web/frontend test:e2e
```
