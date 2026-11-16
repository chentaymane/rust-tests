## Website-style output

Output includes Cargo's full warnings, source locations, error codes and hints,
as in the website tester. Compilation failures end with `Solution did not compile.`

For example, a private `sum` function in `scalar/src/lib.rs` produces diagnostics
like these (excerpt):

```text
warning: function `sum` is never used
error[E0425]: cannot find function `sum` in this scope
 --> src/main.rs:5:25
  |
5 |     println!("sum: {}", sum(234, 2)); // 'sum: 236'
  |                         ^^^ not found in this scope
...
scalar failed
Solution did not compile.
```

The test suite imports your library from a separate crate. Functions required
by the subject must be public, for example `pub fn sum(a: u8, b: u8) -> u8`.
For `scalar`, this also applies to `diff`, `pro`, `quo`, and `rem`.

Passing solutions print Cargo's test results followed by `scalar passed`.
An assertion failure prints the failed test and its assertion details; it is
reported separately from a compilation failure.

The website's `Already failed code at commit` / `Previous output` wrapper belongs
to its submission cache; local runs always test your current saved files.
Local file paths, compiler versions, timings and platform test versions can differ
from the website, so the output is not guaranteed to be byte-for-byte identical.

## Builds and time limits

Your source files are copied into a temporary directory and cleaned up afterward;
build artifacts are cached in the installed tester. Cargo may download dependencies
on first use. Subsequent runs can work offline once those dependencies are cached.
The default limit is 120 seconds per exercise, including compilation/downloads:

```sh
RUST_TEST_TIMEOUT_SECS=300 rt scalar
```

## Update an existing installation

After updating the downloaded tester files, rerun the installer from that directory:

```sh
sh install.sh && . "$HOME/.local/lib/rust-piscine-tester/env"
```

This updates both commands and the installed test bundle. Repeated installation
does not duplicate the startup entries.

If `rt` is unavailable in an already-open terminal, activate its environment:

```sh
. "$HOME/.local/lib/rust-piscine-tester/env"
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
