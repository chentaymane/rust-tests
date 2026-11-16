# Rust piscine local tester

Use `rt` as the short command: `rt`, `rt scalar`, `rt --all`, or `rt --list`.
Both `rt` and `rust-test` are installed and accept the same arguments.

Run the bundled 146 Rust exercise suites locally, without a submission cooldown.
Requires Linux/macOS (or WSL). The installer sets up Rust, Cargo, and missing
system build tools automatically. No Docker or Python is needed for normal use.
Internet access is required if Rust needs installation; installing system build
tools may prompt for your sudo password.

## Install once

From this directory:

```sh
sh install.sh
```

Open a new terminal afterward. The installer configures Bash, Zsh and login-shell
startup files automatically and prints a command to activate the current terminal.
For one command that also activates your current terminal:

```sh
sh install.sh && . "$HOME/.local/lib/rust-piscine-tester/env"
```

Installation copies the tests into `~/.local/lib/rust-piscine-tester`
and the command into `~/.local/bin`; you can then remove the original download.
For another location use `sh install.sh --prefix /your/path`.

## Run from any folder

```sh
cd /path/to/piscine-rust/scalar
rust-test                       # detects scalar, also works inside scalar/src

cd /path/to/piscine-rust
rust-test scalar                # one exercise
rust-test --all                  # all supported exercises found recursively

cd /any/other/folder
rust-test scalar /path/to/piscine-rust
rust-test --all /path/to/piscine-rust
rust-test --list                 # all 146 bundled exercise names
```

Without installation: `sh /path/to/rust-tests/rust-test scalar /path/to/piscine-rust`.
Exercise names accept underscores or hyphens. Use Cargo's usual layout:
`exercise/Cargo.toml` and `exercise/src/lib.rs` (or `src/main.rs` for programs).
A missing manifest is created in the temporary copy. Dependent solved exercises
must be siblings, for example `expected_variable` and `edit_distance`.

Rust prints failed assertions and compilation errors. A nonzero exit code means
failure. `--all` continues after failures and reports passed, failed and skipped
projects. Unsupported projects are explicitly skipped and make the batch exit
nonzero. It tests existing exercises, not missing quests. Run batches on your
piscine directory, not your entire home directory.

Output includes Cargo's full warnings, source locations, error codes and hints,
as in the website tester. Compilation failures end with `Solution did not compile.`
The website's `Already failed code at commit` / `Previous output` wrapper belongs
to its submission cache; local runs always test your current saved files.
Local file paths, compiler versions, timings and platform test versions can differ
from the website, so the output is not guaranteed to be byte-for-byte identical.

Your source files are copied into a temporary directory and cleaned up afterward;
build artifacts are cached in the installed tester. Cargo may download dependencies
on first use. Subsequent runs can work offline once those dependencies are cached.
The default limit is 120 seconds per exercise, including compilation/downloads:

```sh
RUST_TEST_TIMEOUT_SECS=300 rust-test scalar
```

## Coverage and provenance

The linked [01-edu/public](https://github.com/01-edu/public) repository provides
the exercise instructions. This tester reuses the MIT-licensed runner and bundled
tests from [terry-xyz/01-rust-local-test](https://github.com/terry-xyz/01-rust-local-test)
at commit `beba87c81ce49ba59026bebbda5063a1ddbcd1ab`, with automatic detection,
batch testing and a global command installer added here. That bundle records
extraction from the official Rust test image; see [THIRD_PARTY.md](THIRD_PARTY.md)
and [source.json](vendor/01-edu-rust/source.json). The 01-edu test files are
preserved unchanged. `scripts/sync-upstream.py` can restore the recorded image
snapshot with Python and network access.

To refresh directly from the [official container package](https://github.com/orgs/01-edu/packages/container/package/test-rust)
on your PC, without Docker:

```sh
python3 scripts/sync-upstream.py --latest
sh install.sh
```

This downloads the test layers, verifies their SHA-256 digests and records the
image digest in `source.json`. It may change the number of available suites.
The bundled snapshot works immediately; refreshing requires registry access.
The historical hashes in `vendor/snapshot.json` and layer details in
`THIRD_PARTY.md` describe the original bundled version, before a refresh.

This is a snapshot, not a guarantee of matching today's platform grader or every
quest version. Known example: the bundled `hello_rust` assertion expects
`Hello, Rust!!`, while the current public subject says `Hello, Rust!`.
Some exercises require nightly Rust or external crates. Use `--list` to check
available coverage; audit-based projects are outside these automated suites.

The tester executes code with your normal account permissions. Temporary copies
protect your source from tester edits; they do not isolate running code.

## Development checks

```sh
cargo fmt --check
cargo clippy --offline --all-targets -- -D warnings
cargo test --offline
python3 tests/smoke.py
python3 tests/refresh.py
python3 tests/bootstrap.py
```
