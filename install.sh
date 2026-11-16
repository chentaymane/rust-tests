#!/bin/sh
# One-command setup for Linux/macOS/WSL; no manual Rust or PATH setup required.
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
export PATH="$cargo_home/bin:$PATH"

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
if ! command -v cc >/dev/null 2>&1 || { ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; }; then
    install_build_tools
fi
usable_rust() {
    cargo --version >/dev/null 2>&1 && rustc --version >/dev/null 2>&1 &&
        rustc --version | awk '{split($2,v,"."); exit !(v[1]>1 || (v[1]==1 && v[2]>=82))}'
}
if ! usable_rust; then
    if command -v rustup >/dev/null 2>&1; then
        echo 'Setting up the stable Rust toolchain...'
        rustup toolchain install stable --profile minimal
    else
        echo 'Installing Rust and Cargo using the official rustup installer...'
        bootstrap=$(mktemp)
        trap 'rm -f "$bootstrap"' EXIT HUP INT TERM
        if command -v curl >/dev/null 2>&1; then
            curl --proto '=https' --tlsv1.2 -fsSL https://sh.rustup.rs -o "$bootstrap"
        else
            wget -q https://sh.rustup.rs -O "$bootstrap"
        fi
        sh "$bootstrap" -y --profile minimal --default-toolchain stable --no-modify-path
        rm -f "$bootstrap"
        trap - EXIT HUP INT TERM
    fi
    export RUSTUP_TOOLCHAIN=stable
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
cargo build --release --offline --manifest-path "$destination/Cargo.toml" --target-dir "$destination/target"
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
    quote "$destination/target/release/rust-test"; printf ' "$@"\n'
} > "$prefix/bin/rust-test"
chmod +x "$prefix/bin/rust-test"
cp "$prefix/bin/rust-test" "$prefix/bin/rt"
# Configure new login shells and interactive Bash/Zsh shells, without duplicates.
profile_line=". $(quote "$destination/env")"
for startup in "$HOME/.profile" "$HOME/.bashrc" "${ZDOTDIR:-$HOME}/.zshrc"; do
    if ! [ -f "$startup" ] || ! grep -Fqx "$profile_line" "$startup"; then
        printf '\n# Rust piscine local tester\n%s\n' "$profile_line" >> "$startup"
    fi
done
"$prefix/bin/rust-test" --list >/dev/null
printf '\nInstalled and checked: %s/bin/rust-test\n' "$prefix"
printf 'Shortcut: rt (for example: rt --all)\n'
printf 'Open a new terminal and run rt, or activate in this terminal:\n  %s\n' "$profile_line"
