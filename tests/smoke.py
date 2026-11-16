"""End-to-end checks with local fixture solutions; no network dependencies."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd, success=True, env=None):
    result = subprocess.run(
        [str(arg) for arg in args], cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=90,
    )
    assert (result.returncode == 0) == success, result.stdout
    return result.stdout


def snapshot(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='rust-tester-smoke-') as temporary:
        base = Path(temporary)
        prefix = base / 'install with spaces'
        isolated_home = base / 'home'
        isolated_home.mkdir()
        install_env = {
            **os.environ, 'HOME': str(isolated_home),
            'CARGO_HOME': os.environ.get('CARGO_HOME', str(Path.home() / '.cargo')),
            'RUSTUP_HOME': os.environ.get('RUSTUP_HOME', str(Path.home() / '.rustup')),
        }
        run(['sh', ROOT / 'install.sh', '--prefix', prefix], ROOT, env=install_env)
        run(['sh', ROOT / 'install.sh', '--prefix', prefix], ROOT, env=install_env)
        for name in ['.bashrc', '.zshrc', '.profile']:
            assert (isolated_home / name).read_text().count('# Rust piscine local tester') == 1
        binary = prefix / 'bin/rt'
        assert run([binary, '--list'], base) == run([prefix / 'bin/rust-test', '--list'], base)
        listing = run([binary, '--list'], base).splitlines()
        assert len(listing) == 146, len(listing)
        minimal_env = {**install_env, 'PATH': '/usr/bin:/bin'}
        assert len(run([binary, '--list'], base, env=minimal_env).splitlines()) == 146
        piscine = base / 'piscine with spaces'
        scalar = piscine / 'scalar'
        (scalar / 'src').mkdir(parents=True)
        code = '''pub fn sum(a:u8,b:u8)->u8{a+b}
pub fn diff(a:i16,b:i16)->i16{a-b}
pub fn pro(a:i8,b:i8)->i8{a*b}
pub fn quo(a:f32,b:f32)->f32{a/b}
pub fn rem(a:f32,b:f32)->f32{a%b}
'''
        solution = scalar / 'src/lib.rs'
        solution.write_text(code)
        original = snapshot(piscine)
        assert 'scalar passed' in run([binary], scalar / 'src')
        assert 'scalar passed' in run([binary, 'scalar', piscine], base)
        assert '1 passed, 0 failed, 0 skipped' in run([binary, '--all', piscine], base)
        assert original == snapshot(piscine), 'Runner modified student files'
        # Reproduce the website example: private functions are not visible to
        # the separate scalar_test crate. Preserve the real Rust diagnostics.
        solution.write_text(code.replace('pub fn', 'fn'))
        output = run([binary, 'scalar'], piscine, success=False)
        assert 'warning: function `sum` is never used' in output, output
        assert 'error[E0425]: cannot find function `sum` in this scope' in output, output
        assert 'src/main.rs:5:25' in output, output
        assert output.rstrip().endswith('Solution did not compile.'), output
        solution.write_text(code.replace('a+b', '0'))
        output = run([binary, 'scalar'], piscine, success=False)
        assert 'scalar failed' in output
        assert 'Solution did not compile.' not in output
        assert '0 passed, 1 failed' in run([binary, '--all', piscine], base, success=False)
        solution.write_text(code)
        env = {**os.environ, 'RUST_TEST_TIMEOUT_SECS': '0'}
        assert 'positive whole number' in run([binary, 'scalar', piscine], base, False, env)
        unknown = piscine / 'unknown_exercise/src'
        unknown.mkdir(parents=True)
        (unknown / 'lib.rs').write_text('')
        assert '1 passed, 0 failed, 1 skipped' in run([binary, '--all', piscine], base, False)
        assert 'No supported exercises' in run([binary, '--all', base / 'install with spaces/bin'], base, False)
        assert 'No upstream tests' in run([binary, 'does_not_exist', piscine], base, False)
        assert 'Cannot detect' in run([binary], base, False)
        print('Smoke checks passed: installation, detection, pass/fail, batch, skips, source preservation.')


if __name__ == '__main__':
    main()
