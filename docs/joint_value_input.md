# Precise joint value input

Click the numeric field at the right of a joint slider and type a finite number. Negative values and decimals are supported. `Enter` or blur commits, `Escape` restores the value from before editing, and arrow keys or a focused mouse wheel adjust one step. `Shift` uses ten steps and `Alt` one tenth step. `Home`/`End` select finite limits.

Valid text previews immediately in the indexed Three.js joint runtime. Preview does not contact the backend. A completed edit uses the existing batched joint-state endpoint once. Values outside a finite URDF limit are visibly marked while editing and are clamped with an explicit warning on commit. This changes current joint motion, not URDF joint origin.
