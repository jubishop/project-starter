# Maintaining Project Starter

Read [the guide](GUIDE.md) and the relevant [design documents](docs/README.md).
The copyable foundation lives in `starter/`; optional host integration lives
in `extras/`. Keep the guide standalone and free of personal paths or origin
project references. Do not install or register a skill.

Run `bin/check` once for a completed batch of changes. Its tests exercise
copies of the bundle. Reuse a passing result while relevant inputs are
unchanged; discussion and read-only work do not require checks.
Use `bin/smoke-qmd --models /absolute/path/to/existing/models` for explicit
real-QMD validation. Keep copied project behavior and the guide consistent.
