"""Exercise first-install setup offline with a simulated rustup download."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def executable(path, content):
    path.write_text('#!/bin/sh\nset -eu\n' + content)
    path.chmod(0o755)


def main():
    with tempfile.TemporaryDirectory(prefix='rust-bootstrap-') as directory:
        base = Path(directory)
        home = base / 'home'
        home.mkdir()
        fake_bin = base / 'tools'
        fake_bin.mkdir()
        bootstrap = base / 'bootstrap'
        bootstrap.write_text('''#!/bin/sh
set -eu
printf '%s\\n' "$@" > "$HOME/bootstrap-args"
mkdir -p "$HOME/.cargo/bin"
cp "$FIXTURE_CARGO" "$HOME/.cargo/bin/cargo"
cp "$FIXTURE_RUSTC" "$HOME/.cargo/bin/rustc"
''')
        fake_cargo = base / 'fixture-cargo'
        executable(fake_cargo, '''if [ "$1" = --version ]; then echo 'cargo 1.90.0'; exit; fi
while [ "$#" -gt 0 ]; do
    if [ "$1" = --target-dir ]; then shift; output=$1; fi
    shift
done
mkdir -p "$output/release"
printf '#!/bin/sh\\nexit 0\\n' > "$output/release/rust-test"
chmod +x "$output/release/rust-test"
''')
        fake_rustc = base / 'fixture-rustc'
        executable(fake_rustc, "echo 'rustc 1.90.0'\n")
        executable(fake_bin / 'curl', '''while [ "$#" -gt 0 ]; do
    if [ "$1" = -o ]; then shift; output=$1; fi
    shift
done
cp "$FIXTURE_BOOTSTRAP" "$output"
''')
        env = {**os.environ, 'HOME': str(home), 'PATH': f'{fake_bin}:/usr/bin:/bin',
               'FIXTURE_CARGO': str(fake_cargo), 'FIXTURE_RUSTC': str(fake_rustc),
               'FIXTURE_BOOTSTRAP': str(bootstrap)}
        for name in ['CARGO_HOME', 'RUSTUP_HOME', 'RUSTUP_TOOLCHAIN', 'ZDOTDIR']:
            env.pop(name, None)
        prefix = base / "install with 'quotes' and spaces"
        command = ['sh', str(ROOT / 'install.sh'), '--prefix', str(prefix)]
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'Installing Rust and Cargo' in result.stdout
        args = (home / 'bootstrap-args').read_text().splitlines()
        assert args == ['-y', '--profile', 'minimal', '--default-toolchain', 'stable', '--no-modify-path']
        # Source the generated shell configuration using the path as an argument,
        # and check that the installer has configured both Cargo and the tester.
        activation = subprocess.run(
            ['sh', '-c', '. "$1"; command -v cargo; command -v rust-test; rust-test --list',
             'sh', str(prefix / 'lib/rust-piscine-tester/env')],
            env=env, capture_output=True, text=True, timeout=10,
        )
        assert activation.returncode == 0, activation.stdout + activation.stderr
        assert str(prefix / 'bin/rust-test') in activation.stdout
        # A second install must detect the recovered toolchain and keep profiles unique.
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'Installing Rust and Cargo' not in result.stdout
        for name in ['.bashrc', '.zshrc', '.profile']:
            assert (home / name).read_text().count('# Rust piscine local tester') == 1
        print('Bootstrap checks passed: missing Rust, PATH recovery, quoted paths, repeat installation.')


if __name__ == '__main__':
    main()
