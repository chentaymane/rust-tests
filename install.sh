#!/bin/sh
# One-command setup for Linux, macOS, WSL and 64-bit Git Bash on Windows.
set -eu
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
prefix="$HOME/.local"
if [ "$#" -gt 0 ]; then
    if [ "$#" -ne 2 ] || [ "$1" != "--prefix" ]; then
        echo 'Usage: sh install.sh [--prefix PATH]' >&2
        exit 2
    fi
    prefix=$2
fi
cargo_home=${CARGO_HOME:-"$HOME/.cargo"}
exe_suffix=
case "$(uname -s)" in
    MINGW*|MSYS*)
        exe_suffix=.exe
        prefix=$(cygpath -au "$prefix")
        CARGO_HOME=$(cygpath -am "$cargo_home")
        export CARGO_HOME
        cargo_home=$CARGO_HOME
        export PATH="$(cygpath -u "$cargo_home")/bin:$PATH"
        ;;
    *) export PATH="$cargo_home/bin:$PATH" ;;
esac

as_admin() {
    if [ "$(id -u)" -eq 0 ]; then "$@";
    elif command -v sudo >/dev/null 2>&1; then sudo "$@";
    else echo 'Installing system build tools requires sudo or a root account.' >&2; exit 1;
    fi
}
install_build_tools() {
    echo 'Installing compiler, linker and download tools...'
    if command -v apt-get >/dev/null 2>&1; then
        as_admin apt-get update
        as_admin apt-get install -y build-essential curl ca-certificates
    elif command -v dnf >/dev/null 2>&1; then
        as_admin dnf install -y gcc gcc-c++ make curl ca-certificates
    elif command -v pacman >/dev/null 2>&1; then
        as_admin pacman -S --needed --noconfirm base-devel curl ca-certificates
    elif command -v apk >/dev/null 2>&1; then
        as_admin apk add build-base curl ca-certificates
    elif [ "$(uname -s)" = Darwin ]; then
        xcode-select --install || true
        echo 'Finish the Apple Command Line Tools installation, then rerun this command.' >&2
        exit 1
    else
        echo 'No supported package manager found. A C compiler/linker and curl or wget are required.' >&2
        exit 1
    fi
}
# Windows Rust uses its own linker or discovers the installed MSVC tools.
if [ -z "$exe_suffix" ] &&
    { ! command -v cc >/dev/null 2>&1 || { ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; }; }; then
    install_build_tools
fi
usable_rust() {
    cargo --version >/dev/null 2>&1 && rustc --version >/dev/null 2>&1 &&
        rustc --version | awk '{split($2,v,"."); exit !(v[1]>1 || (v[1]==1 && v[2]>=82))}'
}
if ! usable_rust; then
    toolchain=stable
    if [ -n "$exe_suffix" ]; then
        case "$(uname -m)" in
            x86_64) windows_host=x86_64-pc-windows-gnu ;;
            *)
                echo 'Install Rust 1.82 or newer for your Windows architecture from https://rustup.rs/, then rerun this script.' >&2
                exit 1
                ;;
        esac
        toolchain="stable-$windows_host"
    fi
    if command -v rustup >/dev/null 2>&1; then
        printf 'Setting up the %s Rust toolchain...\n' "$toolchain"
        rustup toolchain install "$toolchain" --profile minimal
    else
        echo 'Installing Rust and Cargo using the official rustup installer...'
        bootstrap_dir=$(mktemp -d)
        bootstrap="$bootstrap_dir/rustup-init$exe_suffix"
        trap 'rm -f "$bootstrap"; rmdir "$bootstrap_dir"' EXIT
        trap 'exit 1' HUP INT TERM
        url=https://sh.rustup.rs
        if [ -n "$exe_suffix" ]; then
            url="https://static.rust-lang.org/rustup/dist/$windows_host/rustup-init.exe"
        fi
        if command -v curl >/dev/null 2>&1; then
            curl --proto '=https' --tlsv1.2 -fsSL "$url" -o "$bootstrap"
        elif command -v wget >/dev/null 2>&1; then
            wget -q "$url" -O "$bootstrap"
        else
            echo 'Installing Rust requires curl or wget. Run this script in Git Bash on Windows.' >&2
            exit 1
        fi
        if [ -n "$exe_suffix" ]; then
            chmod +x "$bootstrap"
            "$bootstrap" -y --profile minimal --default-host "$windows_host" --default-toolchain stable --no-modify-path
        else
            sh "$bootstrap" -y --profile minimal --default-toolchain stable --no-modify-path
        fi
        rm -f "$bootstrap"
        rmdir "$bootstrap_dir"
        trap - EXIT HUP INT TERM
    fi
    export RUSTUP_TOOLCHAIN="$toolchain"
fi
usable_rust || { echo 'Rust setup did not complete. Check the download/install messages above.' >&2; exit 1; }
cargo_bin=$(dirname -- "$(command -v cargo)")
mkdir -p "$prefix"
prefix=$(CDPATH= cd -- "$prefix" && pwd)
destination="$prefix/lib/rust-piscine-tester"
if [ "$source_dir" = "$destination" ]; then
    echo 'Run the installer from the original download directory.' >&2
    exit 1
fi
mkdir -p "$destination/src" "$prefix/bin"
cp "$source_dir/Cargo.toml" "$source_dir/THIRD_PARTY.md" "$destination/"
cp "$source_dir/src/main.rs" "$destination/src/"
# Copy the bundle, including its provenance metadata.
mkdir -p "$destination/vendor"
cp -R "$source_dir/vendor/." "$destination/vendor/"
# Override ambient Cargo output directories so the binary has a predictable path.
build_root=$destination
if [ -n "$exe_suffix" ]; then
    build_root=$(cygpath -am "$destination")
fi
cargo build --release --offline --manifest-path "$build_root/Cargo.toml" --target-dir "$build_root/target"
quote() {
    printf "'"
    printf '%s' "$1" | sed "s/'/'\\\\''/g"
    printf "'"
}
# Export Rust locations explicitly; this also fixes Rust installed outside PATH.
{
    printf 'export CARGO_HOME='; quote "$cargo_home"; printf '\n'
    if [ -n "${RUSTUP_HOME:-}" ]; then
        printf 'export RUSTUP_HOME='; quote "$RUSTUP_HOME"; printf '\n'
    fi
    if [ -n "${RUSTUP_TOOLCHAIN:-}" ]; then
        printf 'export RUSTUP_TOOLCHAIN='; quote "$RUSTUP_TOOLCHAIN"; printf '\n'
    fi
    printf 'RUST_TEST_BIN='; quote "$prefix/bin"; printf '\n'
    printf 'RUST_TEST_CARGO_BIN='; quote "$cargo_bin"; printf '\n'
    printf 'export PATH="$RUST_TEST_BIN:$RUST_TEST_CARGO_BIN:$PATH"\n'
} > "$destination/env"
{
    printf '#!/bin/sh\nset -eu\n. '; quote "$destination/env"; printf '\nexec '
    quote "$destination/target/release/rust-test$exe_suffix"; printf ' "$@"\n'
} > "$prefix/bin/rust-test"
chmod +x "$prefix/bin/rust-test"
cp "$prefix/bin/rust-test" "$prefix/bin/rt"
# Configure new login shells and interactive Bash/Zsh shells, without duplicates.
profile_line=". $(quote "$destination/env")"
bash_login="$HOME/.profile"
if [ -n "$exe_suffix" ]; then
    for startup in "$HOME/.bash_profile" "$HOME/.bash_login"; do
        if [ -f "$startup" ]; then
            bash_login=$startup
            break
        fi
    done
fi
for startup in "$bash_login" "$HOME/.bashrc" "${ZDOTDIR:-$HOME}/.zshrc"; do
    if ! [ -f "$startup" ] || ! grep -Fqx "$profile_line" "$startup"; then
        printf '\n# Rust piscine local tester\n%s\n' "$profile_line" >> "$startup"
    fi
done
"$prefix/bin/rust-test" --list >/dev/null
printf '\nInstalled and checked: %s/bin/rust-test\n' "$prefix"
printf 'Shortcut: rt (for example: rt --all)\n'
printf 'Open a new terminal and run rt, or activate in this terminal:\n  %s\n' "$profile_line"
