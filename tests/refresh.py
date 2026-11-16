"""Check registry extraction using synthetic, hashed image layers offline."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sync', ROOT / 'scripts/sync-upstream.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def main():
    registry = {}

    def blob(data):
        digest = 'sha256:' + hashlib.sha256(data).hexdigest()
        registry[f'{sync.REGISTRY}/blobs/{digest}'] = data
        return digest

    layers = []
    for path in ['app/tests/scalar_test/Cargo.toml', 'app/tests_utility/lib/Cargo.toml']:
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w:gz') as archive:
            content = b'[package]\nname="fixture"\nversion="0.1.0"\n'
            entry = tarfile.TarInfo(path)
            entry.size = len(content)
            archive.addfile(entry, io.BytesIO(content))
        layers.append({'digest': blob(stream.getvalue())})
    config = {'history': [{'created_by': f'COPY {name} {name} # buildkit'}
                          for name in ['tests', 'tests_utility']]}
    manifest = json.dumps({'config': {'digest': blob(json.dumps(config).encode())},
                           'layers': layers}).encode()
    registry[f'{sync.REGISTRY}/manifests/latest'] = manifest
    registry[sync.TOKEN_URL] = b'{"token":"fixture"}'
    with tempfile.TemporaryDirectory() as temporary:
        destination = Path(temporary) / 'vendor'
        with patch.object(sync, 'VENDOR', destination), \
                patch.object(sync, 'fetch', side_effect=lambda url, headers=None: registry[url]), \
                patch.object(sys, 'argv', ['sync', '--latest']):
            sync.main()
        assert (destination / 'tests/scalar_test/Cargo.toml').is_file()
        assert (destination / 'tests_utility/lib/Cargo.toml').is_file()
        source = json.loads((destination / 'source.json').read_text())
        assert source['digest'] == 'sha256:' + hashlib.sha256(manifest).hexdigest()
        try:
            sync.verified(b'corrupted', layers[0]['digest'])
        except ValueError:
            pass
        else:
            raise AssertionError('Accepted corrupted layer')
    print('Refresh checks passed: official image layout, extraction and digest validation.')


if __name__ == '__main__':
    main()
