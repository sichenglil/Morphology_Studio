# Joint display units

Rotational joints are stored in radians and can display `rad` or `deg`. Prismatic joints are stored in metres and can display `m`, `cm`, or `mm`. Unit selection only converts display and input steps; it never changes robot pose. Display precision can be 3, 4, or 6 decimals while the internal JavaScript number is retained.

Continuous joints without explicit limits accept any finite input value. Their slider remains a convenient `-π..π` window and does not clamp numeric input.
