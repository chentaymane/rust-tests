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
        checkpoint_exercises = set('''
            min_and_max matrix_multiplication reverse_it smallest modify_letter
            counting_words partial_sums inv_pyramid insertion_sort rpn
            previousprime nextprime count_factorial_steps lucas_number
            own_and_return matrix_determinant check_user_name get_document_id
            dress_code rot21 order_books prime_checker queens scytale_decoder
            negative_spelling office_worker matrix_display organize_garage
            moving_targets format_me blood_types_s car_rental drop_the_blog
            lunch_queue profanity_filter filter_table display_table flat_tree
            brackets_matching brain_fuck
        '''.split())
        missing = checkpoint_exercises - set(listing)
        assert not missing, f'Missing checkpoint suites: {sorted(missing)}'
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
        # Checkpoint submissions are standalone files, without Cargo projects.
        checkpoint = base / 'checkpoint with spaces'
        checkpoint.mkdir()
        single = checkpoint / 'min_and_max.rs'
        correct = 'pub fn min_and_max(a:i32,b:i32,c:i32)->(i32,i32){(a.min(b).min(c),a.max(b).max(c))}\n'
        single.write_text(correct)
        checkpoint_original = snapshot(checkpoint)
        for args, cwd in [
            (['min_and_max.rs'], checkpoint),
            ([single], base),
            (['min_and_max', single], base),
            (['min_and_max.rs', checkpoint], base),
            (['min_and_max'], checkpoint),
        ]:
            assert 'min_and_max passed' in run([binary, *args], cwd)
        assert '1 passed, 0 failed, 0 skipped' in run([binary, '--all', checkpoint], base)
        assert checkpoint_original == snapshot(checkpoint), 'Runner modified checkpoint files'
        assert '--push requires an exercise folder' in run([binary, '-p', single], base, False)
        assert 'No such file' in run([binary, checkpoint / 'nextprime.rs'], base, False)
        single.write_text(correct.replace('(a.min(b).min(c),a.max(b).max(c))', '(0,0)'))
        assert 'min_and_max failed' in run([binary, single], base, False)
        single.write_text('invalid rust syntax')
        assert 'Solution did not compile.' in run([binary, single], base, False)
        single.write_text(correct)
        # Program exercises must be staged as binaries, rather than libraries.
        rpn = checkpoint / 'rpn.rs'
        rpn.write_text('''fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    let result = (|| -> Option<i64> {
        if args.len() != 1 { return None; }
        let mut stack = Vec::new();
        for token in args[0].split_whitespace() {
            if let Ok(n) = token.parse::<i64>() { stack.push(n); }
            else {
                let b = stack.pop()?;
                let a = stack.pop()?;
                stack.push(match token {
                    "+" => a.checked_add(b)?, "-" => a.checked_sub(b)?,
                    "*" => a.checked_mul(b)?, "/" => a.checked_div(b)?,
                    "%" => a.checked_rem(b)?, _ => return None,
                });
            }
        }
        if stack.len() == 1 { stack.pop() } else { None }
    })();
    match result { Some(n) => println!("{n}"), None => println!("Error") }
}
''')
        assert 'rpn passed' in run([binary, rpn], base)
        # Exercise pushes use only temporary repositories and a local bare remote.
        remote = base / 'remote.git'
        run(['git', 'init', '--bare', remote], base)
        run(['git', 'init', piscine], base)

        def git(*args, success=True):
            return run(['git', *args], piscine, success=success)

        git('config', 'user.name', 'Tester')
        git('config', 'user.email', 'tester@example.invalid')
        git('config', 'commit.gpgsign', 'false')
        git('add', '.')
        git('commit', '-m', 'initial')
        git('remote', 'add', 'origin', str(remote))
        git('push', '-u', 'origin', 'HEAD')
        unrelated = piscine / 'notes.txt'
        unrelated.write_text('Keep staged but out of the exercise commit.\n')
        git('add', 'notes.txt')
        solution.write_text(code.replace('a+b', '0'))
        before_head = git('rev-parse', 'HEAD')
        before_index = git('diff', '--cached')
        assert 'scalar failed' in run([binary, '-p', 'scalar'], piscine, False)
        assert before_head == git('rev-parse', 'HEAD')
        assert before_index == git('diff', '--cached'), 'Failed tests changed the index'
        assert not (scalar / '.gitignore').exists(), 'Failed tests changed ignore rules'
        artifact = scalar / 'target/debug/build-artifact'
        artifact.parent.mkdir(parents=True)
        artifact.write_bytes(b'local build output')
        (scalar / '.gitignore').write_text('# preserve existing rules\n*.swp')
        solution.write_text(code + '// ready to submit\n')
        assert 'scalar passed' in run([binary, '--push', 'scalar'], piscine)
        assert git('log', '-1', '--format=%s').strip() == 'scalar'
        assert git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines() == ['scalar/.gitignore', 'scalar/src/lib.rs']
        assert (scalar / '.gitignore').read_text() == '# preserve existing rules\n*.swp\ntarget/\n'
        assert not git('ls-files', '--', 'scalar/target')
        assert artifact.read_bytes() == b'local build output'
        assert git('check-ignore', 'scalar/target/debug/build-artifact').strip() == 'scalar/target/debug/build-artifact'
        assert git('diff', '--cached', '--name-only').splitlines() == ['notes.txt']
        assert git('rev-parse', 'HEAD') == git('rev-parse', '@{upstream}')
        committed = git('rev-parse', 'HEAD')
        assert 'No changes' in run([binary, '-p'], scalar / 'src')
        assert committed == git('rev-parse', 'HEAD'), 'Retry created a duplicate commit'
        # Repair build files committed by an older rt; preserve them on disk.
        git('add', '-f', 'scalar/target')
        git('commit', '--only', '-m', 'old build artifacts', '--', 'scalar/target')
        artifact.write_bytes(b'updated local build output')
        git('add', '-f', 'scalar/target')
        assert 'scalar passed' in run([binary, '-p', 'scalar'], piscine)
        assert not git('ls-tree', '-r', '--name-only', 'HEAD', '--', 'scalar/target')
        assert not git('ls-files', '--', 'scalar/target')
        assert artifact.read_bytes() == b'updated local build output'
        assert git('diff', '--cached', '--name-only').splitlines() == ['notes.txt']
        committed = git('rev-parse', 'HEAD')
        # A failed push keeps its commit, allowing a later retry with no changes.
        git('remote', 'set-url', 'origin', str(base / 'missing-remote'))
        solution.write_text(code + '// another submission\n')
        assert 'git push failed' in run([binary, '-p', scalar], base, False)
        local_commit = git('rev-parse', 'HEAD')
        assert local_commit != committed
        assert committed == git('rev-parse', '@{upstream}')
        git('remote', 'set-url', 'origin', str(remote))
        assert 'No changes' in run([binary, '--push', scalar], base)
        assert local_commit == git('rev-parse', 'HEAD') == git('rev-parse', '@{upstream}')
        assert git('diff', '--cached', '--name-only').splitlines() == ['notes.txt']
        for invalid in ['--all', '--list', '-p']:
            assert 'usage:' in run([binary, '-p', invalid], piscine, False)
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
        print('Smoke checks passed: installation, detection, pass/fail, batch, skips, source preservation, Git push workflow.')


if __name__ == '__main__':
    main()
