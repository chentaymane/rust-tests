# Third-party code

Runner adapted from https://github.com/terry-xyz/01-rust-local-test,
commit beba87c81ce49ba59026bebbda5063a1ddbcd1ab (MIT; notice reproduced below).
Local additions include exercise detection, batch execution, installation,
and an optional refresh from the official container package.

The following notice applies to code reused from that upstream project.
Vendored files retain their upstream terms and notices; this is not a
project-wide license for local additions.

Files under `vendor/01-edu-rust/tests` and `vendor/01-edu-rust/tests_utility`
are copied unchanged from the official `ghcr.io/01-edu/test-rust` image.

- Source: [01-edu/rust-tests](https://github.com/01-edu/rust-tests).
- Image digest: `sha256:979f5a497a90eb55ce610afcf87cdd01fea1ca8694a9cc98e6db22c028ea3e82`.
- Test layer: `sha256:6f1d13ef83e2b8e21e9f0d0e9e2225e88a71a61916af45cfc24410c5fc4c587c`.
- Helper layer: `sha256:22e30301760f2acfc7c559755ed79532969b8ee607643a0a25dd1c53d78f4ba6`.
- The official image declares `org.opencontainers.image.licenses=MIT`.

Only test suites and their helper are included. The runner adjusts the layout
and Cargo settings in a temporary copy; vendored files remain unchanged.
[scripts/sync-upstream.py](scripts/sync-upstream.py) reproduces the extraction
from the pinned image without running Docker.


## Upstream runner license notice

```text
MIT License

Copyright (c) 2026 Lefteris Papanthymou

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
