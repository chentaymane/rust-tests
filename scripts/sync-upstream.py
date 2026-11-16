"""Restore the pinned official test files; no Docker daemon is required."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import shutil
import tempfile
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "01-edu-rust"
SOURCE = json.loads((VENDOR / "source.json").read_text())
TOKEN_URL = "https://ghcr.io/token?scope=repository:01-edu/test-rust:pull"
REGISTRY = "https://ghcr.io/v2/01-edu/test-rust"


def fetch(url, headers=None):
    with urlopen(Request(url, headers=headers or {}), timeout=60) as response:
        return response.read()


def verified(data, digest):
    if "sha256:" + hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"Digest mismatch: {digest}")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--latest', action='store_true',
                        help='Refresh from the official latest image instead of restoring the pinned snapshot')
    args = parser.parse_args()
    source = dict(SOURCE)
    token = json.loads(fetch(TOKEN_URL))["token"]
    headers = {"Authorization": f"Bearer {token}"}
    accept = ', '.join((
        'application/vnd.docker.distribution.manifest.v2+json',
        'application/vnd.oci.image.manifest.v1+json',
        'application/vnd.docker.distribution.manifest.list.v2+json',
        'application/vnd.oci.image.index.v1+json',
    ))
    reference = 'latest' if args.latest else source['digest']
    data = fetch(f"{REGISTRY}/manifests/{reference}", {**headers, 'Accept': accept})
    if not args.latest:
        verified(data, source['digest'])
    source['digest'] = 'sha256:' + hashlib.sha256(data).hexdigest()
    manifest = json.loads(data)
    if 'manifests' in manifest:
        platform = next((item for item in manifest['manifests']
                         if item.get('platform', {}).get('os') == 'linux'
                         and item.get('platform', {}).get('architecture') == 'amd64'), None)
        if platform is None:
            raise ValueError('No Linux amd64 test image found')
        digest = platform['digest']
        data = verified(fetch(f"{REGISTRY}/manifests/{digest}",
                              {**headers, 'Accept': accept}), digest)
        manifest = json.loads(data)
    config_digest = manifest["config"]["digest"]
    config = json.loads(verified(fetch(f"{REGISTRY}/blobs/{config_digest}", headers), config_digest))
    layers = iter(manifest["layers"])
    with tempfile.TemporaryDirectory(prefix="rust-tests-refresh-") as temporary:
        staging = Path(temporary)
        copied = 0
        found = set()
        for history in config["history"]:
            if history.get("empty_layer", False):
                continue
            layer = next(layers)
            command = history.get("created_by", "")
            prefix = next((prefix for copy, prefix in (
                ("COPY tests tests", "app/tests/"),
                ("COPY tests_utility tests_utility", "app/tests_utility/"),
            ) if command.startswith(copy + " ")), None)
            if prefix is None:
                continue
            found.add(prefix)
            digest = layer["digest"]
            data = verified(fetch(f"{REGISTRY}/blobs/{digest}", headers), digest)
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
                for member in archive:
                    if not member.name.startswith(prefix) or not member.isfile():
                        continue
                    target = (staging / member.name.removeprefix("app/")).resolve()
                    if not target.is_relative_to(staging.resolve()):
                        raise ValueError(f"Unsafe archive path: {member.name}")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
                    copied += 1
        if found != {"app/tests/", "app/tests_utility/"}:
            raise ValueError("Official test layers not found in image")
        # Download and validate both trees before replacing the installed snapshot.
        for name in ('tests', 'tests_utility'):
            if not (staging / name).is_dir():
                raise ValueError(f'Missing extracted directory: {name}')
        suites = list((staging / 'tests').glob('*_test/Cargo.toml'))
        if not suites:
            raise ValueError('Image contains no exercise suites')
        VENDOR.mkdir(parents=True, exist_ok=True)
        for name in ('tests', 'tests_utility'):
            destination = VENDOR / name
            backup = VENDOR / (name + '.previous')
            if backup.exists():
                raise ValueError(f'Remove or restore existing backup first: {backup}')
            if destination.exists():
                destination.rename(backup)
            try:
                shutil.move(str(staging / name), str(destination))
            except Exception:
                if backup.exists():
                    backup.rename(destination)
                raise
            if backup.exists():
                shutil.rmtree(backup)
    (VENDOR / 'source.json').write_text(json.dumps(source, indent=2) + '\n')
    print(f"Restored {copied} official files ({len(suites)} suites) from {source['image']}@{source['digest']}")


if __name__ == "__main__":
    try:
        main()
    except (URLError, ValueError, KeyError, OSError) as error:
        raise SystemExit(f'Could not refresh official tests: {error}') from None

