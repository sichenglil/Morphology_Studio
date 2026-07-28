# Joint rendering baseline

The pre-optimization audit found a deterministic 1:1 relationship between slider inputs, backend PATCHes,
scene rebuilds and complete resource-loader passes. A 1000-event synthetic interaction therefore produced
1000 requests and 1000 rebuilds; UR5e re-requested its visual resources on every completed response.

The optimized benchmark records measured local timings in `build/performance/after.json`; architecture
counters are the portable comparison because browser FPS is hardware-dependent. See
`docs/performance_benchmark.md` for the final table and commands.
