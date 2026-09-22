import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Generator, Literal
from urllib.parse import urlparse

from benedict import benedict
import polars as pl


lg = logging.getLogger('fvc.tools.df')

#: Default S3 root used to resolve relative fetch URIs.
DEFAULT_S3_ROOT = 's3://flyvercity.datasets/'


class JsonlinesIO:
    def __init__(
        self,
        filepath: Path,
        mode: Literal['r', 'w'],
        callback=None,
        raw: bool = False,
    ):
        self._filepath = filepath
        self._mode = mode
        self._file = None  # IO | None
        self._callback = callback
        self._pos = 0
        # Performance optimization: if True, skip benedict wrapping for read operations
        self._raw = raw

    def stat_size(self):
        # NOTE: This is used by external code, do not delete
        return self._filepath.stat().st_size

    def __enter__(self):
        self._file = self._filepath.open(f'{self._mode}t', encoding='utf-8', newline=None)
        self._in_line_no = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._file:
            self._file.close()

    def _check_entered(self):
        if not self._file:
            raise UserWarning('Enter context before using the object')

    def read(self) -> benedict | dict | None:
        self._check_entered()

        if self._file:
            line = self._file.readline()
        else:
            raise RuntimeError('File is not open')

        self._in_line_no += 1

        if self._callback:
            new_pos = self._file.tell()
            self._callback(new_pos - self._pos)
            self._pos = new_pos

        if not line.strip():
            return None

        data = json.loads(line)

        if self._raw:
            # Skip benedict wrapping for performance
            return data

        return benedict(data)

    def in_line_no(self):
        return self._in_line_no

    def write(self, data):
        self._check_entered()

        if self._file:
            line = json.dumps(data) + '\n'
            self._file.write(line)

            if self._callback:
                self._callback(len(line.encode('utf-8')))
        else:
            raise RuntimeError('File is not open')

    def write_dataframe(self, df: pl.DataFrame):
        """Write a Polars DataFrame as JSON lines to the file."""
        self._check_entered()

        if self._file:
            df.write_ndjson(self._file)
        else:
            raise RuntimeError('File is not open')

    def read_dataframe(self) -> pl.DataFrame:
        """Read remaining JSON lines from the file as a Polars DataFrame."""
        self._check_entered()

        if self._file:
            return pl.read_ndjson(self._file)

        raise RuntimeError('File is not open')

    def iterate(self) -> Generator[benedict | dict, None, None]:
        while data := self.read():
            yield data


def parse_uri(uri: str, s3_root: str = DEFAULT_S3_ROOT) -> tuple[str, str] | None:
    """Resolve a fetch URI into an ``(bucket, key)`` pair.

    Args:
        uri: Either a full ``s3://bucket/key`` URI or a relative path that is
            joined onto ``s3_root``.
        s3_root: The default S3 root (``s3://bucket/prefix``) used to resolve
            relative paths.

    Returns:
        A ``(bucket, key)`` tuple for S3 URIs, or ``None`` when ``uri`` refers
        to an existing local path (so callers can use it as-is).

    Raises:
        UserWarning: If the URI is empty or cannot be resolved to a valid
            ``s3://bucket/key`` location.
    """

    if not uri:
        raise UserWarning('Empty URI provided')

    parsed = urlparse(uri)

    if parsed.scheme == 's3':
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')

        if not bucket or not key:
            raise UserWarning(f'Invalid S3 URI: {uri}')

        return bucket, key

    # Backward compatibility: an existing local path is used directly.
    if Path(uri).exists():
        return None

    # Treat as a relative path against the default S3 root.
    root = urlparse(s3_root)

    if root.scheme != 's3' or not root.netloc:
        raise UserWarning(f'Invalid S3 root: {s3_root}')

    bucket = root.netloc
    prefix = root.path.strip('/')
    rel = uri.strip('/')
    key = f'{prefix}/{rel}' if prefix else rel

    if not key:
        raise UserWarning(f'Cannot resolve URI: {uri}')

    return bucket, key


def default_bucket(s3_root: str = DEFAULT_S3_ROOT) -> str:
    """Return the bucket name of the default S3 root."""

    return urlparse(s3_root).netloc


def cache_target(bucket: str, key: str, cache_dir: Path, s3_root: str = DEFAULT_S3_ROOT) -> Path:
    """Return the local cache path for ``s3://bucket/key``.

    The cache root mirrors the default bucket's root, so keys from the default
    bucket map directly to ``cache_dir/key`` (no redundant bucket directory).
    Keys from any other bucket are namespaced under ``cache_dir/bucket/key`` to
    avoid collisions.
    """

    if bucket == default_bucket(s3_root):
        return Path(cache_dir) / key

    return Path(cache_dir) / bucket / key


def fetch(
    uri: str,
    cache_dir: Path | None = None,
    s3_root: str = DEFAULT_S3_ROOT,
    force: bool = False,
) -> Path:
    """Resolve ``uri`` to a local path, downloading from S3 if needed.

    Full ``s3://`` URIs and relative paths (resolved against ``s3_root``) are
    downloaded into ``cache_dir``. The cache root mirrors the default bucket's
    root, so keys from the default bucket map to ``cache_dir/key``; keys from
    other buckets are namespaced under ``cache_dir/bucket/key``. Existing local
    paths are returned unchanged.

    AWS credentials are resolved via the standard boto3 chain, honouring the
    ``AWS_PROFILE`` environment variable (which the top-level ``--aws-profile``
    option sets).

    Args:
        uri: The file URI (``s3://bucket/key`` or a relative cache path).
        cache_dir: The local cache root (``FVC_CACHE`` / ``--cache-dir``).
        s3_root: Default S3 root for relative URIs.
        force: Re-download even if a cached copy already exists.

    Returns:
        The local :class:`~pathlib.Path` of the resolved file.

    Raises:
        UserWarning: If the cache directory is missing or the download fails.
    """

    resolved = parse_uri(uri, s3_root)

    if resolved is None:
        # Existing local path, used directly.
        return Path(uri)

    bucket, key = resolved

    cache_dir = cache_dir or os.getenv('FVC_CACHE')

    if not cache_dir:
        raise UserWarning('Cache directory is not set, use --cache-dir or FVC_CACHE')

    target = cache_target(bucket, key, cache_dir, s3_root)

    if target.exists() and not force:
        lg.debug(f'Using cached file: {target}')
        return target

    target.parent.mkdir(parents=True, exist_ok=True)

    lg.info(f'Downloading s3://{bucket}/{key} to {target}')

    try:
        import boto3
        from botocore.exceptions import NoCredentialsError

        s3 = boto3.client('s3')
        s3.download_file(bucket, key, str(target))

    except NoCredentialsError:
        raise UserWarning(
            'Unable to locate AWS credentials. Pass --aws-profile <name>, set the '
            'AWS_PROFILE environment variable, or configure default credentials.'
        )

    except Exception as e:
        raise UserWarning(f'Failed to download s3://{bucket}/{key}: {e}')

    return target


def input_path(params: benedict) -> Path:
    param = params.get('input_path')

    if not param:
        raise UserWarning('Input path is not set, use --in to set it')

    path = fetch(
        str(param),
        params.get('cache_dir'),
        params.get('s3_root', DEFAULT_S3_ROOT),
    )

    if suffix := params.get('suffix'):
        path = path.with_suffix(suffix)

    return path


@dataclass(frozen=True, eq=False, repr=False)
class FvcDataset:
    metadata: benedict
    df: pl.DataFrame

    @staticmethod
    def read(filepath: Path) -> 'FvcDataset':
        with JsonlinesIO(filepath, 'r') as io:
            metadata = io.read()
            df = io.read_dataframe()
            return FvcDataset(metadata, df)
