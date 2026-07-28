# Link panel scrolling acceptance

## Results

The real-browser fixture contains 100 Links and 99 fixed Joints. At 1440×900, Links displayed about seven complete rows at once; its measured viewport was 247 px high with a 3504 px scroll extent. The browser rendered all 100 rows, mouse-wheel scrolling changed the visible range, and `End` selected and revealed `link_99`.

Unit coverage also exercised 500 and 1000 links. Both crossed the 200-link virtualization threshold, kept the full logical count, rendered fewer than 50 active DOM rows, and allowed keyboard selection of the final 1000-link item.

| Acceptance | Result |
|---|---|
| 100-link wheel, bottom and selection | PASS |
| 500-link virtual list | PASS |
| 1000-link virtual list and End selection | PASS |
| Resources accessible and independently laid out | PASS |
| Semantics accessible and independently laid out | PASS |
| Tab switch preserves Links scrollTop | PASS |
| 1100×700 compact window | PASS |
| 1440×900 normal window | PASS |
| 1920×1080 large window | PASS |
| Sidebar wheel leaves viewport pixels unchanged | PASS |
| Canvas wheel still zooms OrbitControls | PASS |
| Browser production-static mode | PASS |
| Local desktop/PyInstaller mode | PASS: rebuilt EXE, native process, `/api/health`, file logging |
| ROS 2 / Isaac | NOT_AVAILABLE_LOCAL |

Screenshots are stored in `build/ui/acceptance/scroll-panels/`: `links_top.png`, `links_middle.png`, `links_bottom.png`, `last_link_selected.png`, `resources_visible.png`, `semantics_visible.png`, `compact_window.png`, `large_window.png`, and `scroll_not_affecting_viewport.png`.

Windows scaling at 125% and 150% was not physically switchable from automation. Responsive viewport tests cover the requested pixel layouts, but native DPI switching remains a manual acceptance item.
