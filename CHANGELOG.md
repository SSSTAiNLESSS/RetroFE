# Changelog: Feature/Data-Modernization

**This branch is the CORE baseline** — the branch the live arcade `retrofe.exe` is built from,
and the default parent for new feature branches. It carries the mixed-collections and libVLC work
it descends from, plus the first scaffolding for the Arrow/DuckDB data layer described in
`docs/RetroFE/RetroFE Modernization and Performance.md`.

## [feature/data-modernization]

### Added
- **Modernization roadmap** (`docs/RetroFE/RetroFE Modernization and Performance.md`): the phased
  plan for Arrow/Parquet columnar storage, DuckDB smart playlists, Rust modules via cxx, libmpv
  rendering, UI virtualization and an expanded metadata schema.
- **`RustCore/` scaffold**: `Cargo.toml`, `build.rs`, `lib.rs` and a `cxx` bridge, targeting
  arrow 53.3 / parquet 53.3 / duckdb 1.1.3.
- **Metadata backend interface**: `Database/IMetadataBackend.h` and
  `Database/SQLiteMetadataBackend.h`, the seam that lets the current SQLite store be swapped for
  an Arrow-backed one without touching call sites.
- **Project documentation on the baseline** (`06a32d7`): `HANDOVER.md`,
  `docs/RetroFE/Git-Operating-Procedure.md` and the modernization roadmap now live here, so every
  branch cut from this one inherits them. They previously existed only on
  `feature/layout-hot-reload`, which meant a new branch started with no handover and no procedure.

### Fixed
- **VLC videos not looping** (`76e344d`): videos played once and then froze.

### Changed
- **`.gitignore` hardened**: ignores `RustCore/target/`, which reaches **2.2 GB** when DuckDB
  builds from source under the `bundled` feature; `=*`, which catches files created by unquoted
  shell redirects; and encodes the partial-tracking rule for `docs/` with a comment naming which
  files sit on each side of the line.

### ⚠️ Status of the Rust work
**`RustCore/` is an early scaffold, not working code.** `CMakeLists.txt` contains no reference to
`RustCore`, `retrofe-core` or `cargo` — the crate does not participate in the C++ build and
changes no runtime behaviour. Wiring it into CMake is unstarted. Anything describing this branch
as "Rust-integrated" is overstating it.

### Note
This branch descends from `feature/mixed-collections`, so it also contains the mixed-system
collection support and the libVLC video backend. A PR from here would carry all of that; see
`HANDOVER.md` §7 for the clean-branch recipe if one is ever wanted.
