# Rust piscine & checkpoint tester

146 bundled test suites, including all **40 Rust checkpoint exercises**.
Linux, macOS, WSL and 64-bit Windows (x86-64) with Git Bash.
`rt` and `rust-test` accept the same commands.

## Install or update

Run from the downloaded tester directory. On Windows, use Git Bash:

```sh
sh install.sh && . "$HOME/.local/lib/rust-piscine-tester/env"
```

Sets up Rust, tests and commands. No Docker or Python needed.
Downloads require internet. On Linux and macOS, system build tools may require
sudo. On macOS, finish Command Line Tools installation if prompted, then rerun.

On Windows, a fresh install uses Rust's GNU toolchain with its bundled linker.
Existing MSVC toolchains need the
[Visual Studio C++ build tools and Windows SDK](https://rust-lang.github.io/rustup/installation/windows-msvc.html).

## Checkpoints: test a file or Cargo project

No `Cargo.toml` or `src/` folder needed:

```sh
cd /path/to/checkpoint
rt min_and_max.rs
rt matrix_multiplication.rs
rt rpn.rs
rt --all                         # test exercise files and projects in this directory
```

From another directory:

```sh
rt /path/to/checkpoint/min_and_max.rs
rt min_and_max /path/to/checkpoint/min_and_max.rs
rt --all /path/to/checkpoint
```

To test a Cargo project, pass its directory or run `rt` from inside an
exercise-named project:

```sh
rt /path/to/checkpoint/min_and_max
rt min_and_max /path/to/project
cd /path/to/checkpoint/min_and_max
rt
```

Name each standalone file after its exercise. Library exercises need public
functions and a matching Cargo package name. You can put those functions in
`src/lib.rs` or in `src/main.rs` of a standard `cargo new` project. Program
exercises such as `rpn` need `fn main()` in `src/main.rs` for a Cargo project.
Required solved dependencies can be sibling `.rs` files or exercise folders.
The tester copies submissions into a temporary directory.

[Checkpoint levels, XP and exercise lists](CHECKPOINTS.md)

## Piscine: test an exercise folder

```sh
cd /path/to/piscine-rust
rt scalar                        # scalar/src/lib.rs
rt --all                         # recursively test available exercises
rt scalar /path/to/piscine-rust

cd scalar/src
rt                               # detect the current exercise
```

Supports `exercise/src/lib.rs` or `src/main.rs`; a missing manifest is generated
in the temporary copy. Exercise names accept underscores or hyphens.

## Commands

| Command | Action |
| --- | --- |
| `rt min_and_max.rs` | Test a standalone checkpoint file |
| `rt ./min_and_max` | Test a checkpoint Cargo project |
| `rt scalar` | Test an exercise folder (or `scalar.rs` if present) |
| `rt --all [directory]` | Test files and folders; report passed, failed, skipped |
| `rt --list` | List bundled exercises |
| `rt -p scalar` | Test, then add, commit and push the exercise folder |
| `rt -p` | Detect, test and push the current exercise folder |
| `RUST_TEST_TIMEOUT_SECS=300 rt scalar` | Set a 300-second limit (default: 120) |

Push mode requires an exercise folder and configured Git remote/upstream.
The commit message is the folder name. Other staged files stay staged.
Failed tests never run Git commands; failed pushes keep the local commit.
Exercise `target/` files are ignored and untracked, remaining on disk.
Pushing also sends any earlier unpushed commits on the branch.

## Results and setup notes

- Success: `<exercise> passed`. Compilation failure: `Solution did not compile.`
- Cargo warnings and assertion details are shown. Failures return a nonzero exit code.
- `--all` continues after failures; unsupported exercises are skipped and return nonzero.
- First runs may download dependencies; later runs can work offline if cached.
- Commands install to `~/.local/bin`; tests to `~/.local/lib/rust-piscine-tester`.
- Custom location: `sh install.sh --prefix /your/path`.
- On Windows with Rust's GNU toolchain, use an install path without apostrophes so the linker can build exercises.
- Without installing: `sh /path/to/rust-tests/rust-test min_and_max.rs`.
- If `rt` is missing: `. "$HOME/.local/lib/rust-piscine-tester/env"`.

## Coverage and provenance

Tests are a snapshot and may differ from the platform grader. Some require
external crates or nightly Rust; audit projects are excluded. Submitted code
runs with your account permissions.

[Upstream sources and license](THIRD_PARTY.md) ·
[Diagnostics, test refresh and development checks](DETAILS.md)
