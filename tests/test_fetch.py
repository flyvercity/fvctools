from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fvc.tools.df import utils as dfu


# --- parse_uri ---------------------------------------------------------------


def test_parse_uri_full_s3():
    assert dfu.parse_uri('s3://mybucket/path/to/file.fvc') == ('mybucket', 'path/to/file.fvc')


def test_parse_uri_relative_default_root():
    # DEFAULT_S3_ROOT has no prefix, just the bucket.
    assert dfu.parse_uri('flights/flight.fvc') == ('flyvercity.datasets', 'flights/flight.fvc')


def test_parse_uri_relative_custom_root():
    bucket, key = dfu.parse_uri('flight.fvc', s3_root='s3://custom.bucket/data/')
    assert (bucket, key) == ('custom.bucket', 'data/flight.fvc')


def test_parse_uri_relative_leading_slash_normalized():
    bucket, key = dfu.parse_uri('/flight.fvc', s3_root='s3://custom.bucket/data')
    assert (bucket, key) == ('custom.bucket', 'data/flight.fvc')


def test_parse_uri_existing_local_path_returns_none(tmp_path):
    local = tmp_path / 'local.fvc'
    local.write_text('{}', encoding='utf-8')
    assert dfu.parse_uri(str(local)) is None


def test_parse_uri_empty_raises():
    with pytest.raises(UserWarning):
        dfu.parse_uri('')


def test_parse_uri_invalid_s3_raises():
    with pytest.raises(UserWarning):
        dfu.parse_uri('s3://bucket-only')


def test_parse_uri_invalid_root_raises():
    with pytest.raises(UserWarning):
        dfu.parse_uri('flight.fvc', s3_root='not-a-uri')


# --- cache_target ------------------------------------------------------------


def test_cache_target_other_bucket_keeps_bucket_dir():
    target = dfu.cache_target('bucket', 'a/b/file.fvc', Path('/cache'))
    assert target == Path('/cache') / 'bucket' / 'a' / 'b' / 'file.fvc'


def test_cache_target_default_bucket_drops_bucket_dir():
    target = dfu.cache_target('flyvercity.datasets', 'a/b/file.fvc', Path('/cache'))
    assert target == Path('/cache') / 'a' / 'b' / 'file.fvc'


def test_cache_target_custom_root_default_bucket():
    target = dfu.cache_target('custom.bucket', 'a/file.fvc', Path('/cache'), s3_root='s3://custom.bucket/')
    assert target == Path('/cache') / 'a' / 'file.fvc'


# --- fetch -------------------------------------------------------------------


def test_fetch_downloads_s3(tmp_path):
    cache = tmp_path / 'cache'
    mock_s3 = MagicMock()

    with patch('boto3.client', return_value=mock_s3) as mock_client:
        result = dfu.fetch('s3://bucket/data/flight.fvc', cache, force=False)

    expected = cache / 'bucket' / 'data' / 'flight.fvc'
    assert result == expected
    assert expected.parent.exists()
    mock_client.assert_called_once_with('s3')
    mock_s3.download_file.assert_called_once_with('bucket', 'data/flight.fvc', str(expected))


def test_fetch_cache_hit_skips_download(tmp_path):
    cache = tmp_path / 'cache'
    target = cache / 'bucket' / 'flight.fvc'
    target.parent.mkdir(parents=True)
    target.write_text('cached', encoding='utf-8')

    with patch('boto3.client') as mock_client:
        result = dfu.fetch('s3://bucket/flight.fvc', cache)

    assert result == target
    mock_client.assert_not_called()


def test_fetch_force_redownloads(tmp_path):
    cache = tmp_path / 'cache'
    target = cache / 'bucket' / 'flight.fvc'
    target.parent.mkdir(parents=True)
    target.write_text('cached', encoding='utf-8')

    mock_s3 = MagicMock()
    with patch('boto3.client', return_value=mock_s3):
        result = dfu.fetch('s3://bucket/flight.fvc', cache, force=True)

    assert result == target
    mock_s3.download_file.assert_called_once()


def test_fetch_local_path_passthrough(tmp_path):
    local = tmp_path / 'local.fvc'
    local.write_text('{}', encoding='utf-8')

    with patch('boto3.client') as mock_client:
        result = dfu.fetch(str(local), tmp_path / 'cache')

    assert result == local
    mock_client.assert_not_called()


def test_fetch_relative_uses_default_root(tmp_path):
    cache = tmp_path / 'cache'
    mock_s3 = MagicMock()

    with patch('boto3.client', return_value=mock_s3):
        result = dfu.fetch('flights/flight.fvc', cache)

    # Default bucket -> no redundant bucket directory in the cache.
    expected = cache / 'flights' / 'flight.fvc'
    assert result == expected
    mock_s3.download_file.assert_called_once_with('flyvercity.datasets', 'flights/flight.fvc', str(expected))


def test_fetch_default_bucket_full_uri_drops_bucket_dir(tmp_path):
    cache = tmp_path / 'cache'
    mock_s3 = MagicMock()

    with patch('boto3.client', return_value=mock_s3):
        result = dfu.fetch('s3://flyvercity.datasets/flights/flight.fvc', cache)

    assert result == cache / 'flights' / 'flight.fvc'


def test_fetch_no_credentials_gives_clear_error(tmp_path):
    from botocore.exceptions import NoCredentialsError

    cache = tmp_path / 'cache'
    mock_s3 = MagicMock()
    mock_s3.download_file.side_effect = NoCredentialsError()

    with patch('boto3.client', return_value=mock_s3):
        with pytest.raises(UserWarning, match='credentials'):
            dfu.fetch('s3://bucket/flight.fvc', cache)


def test_fetch_missing_cache_dir_raises(tmp_path):
    with pytest.raises(UserWarning):
        dfu.fetch('s3://bucket/flight.fvc', None)


def test_fetch_download_error_raises(tmp_path):
    cache = tmp_path / 'cache'
    mock_s3 = MagicMock()
    mock_s3.download_file.side_effect = RuntimeError('boom')

    with patch('boto3.client', return_value=mock_s3):
        with pytest.raises(UserWarning):
            dfu.fetch('s3://bucket/flight.fvc', cache)


# --- global --aws-profile sets AWS_PROFILE -----------------------------------


def test_aws_profile_sets_env_var(monkeypatch):
    from click.testing import CliRunner

    from fvc.tools.cli import cli

    monkeypatch.delenv('AWS_PROFILE', raising=False)
    captured = {}

    @cli.command(name='_probe')
    def _probe():
        import os

        captured['AWS_PROFILE'] = os.environ.get('AWS_PROFILE')

    runner = CliRunner()
    result = runner.invoke(cli, ['--aws-profile', 'flyvercity', '_probe'])

    assert result.exit_code == 0, result.output
    assert captured['AWS_PROFILE'] == 'flyvercity'


# --- input_path integration --------------------------------------------------


def test_input_path_resolves_s3(tmp_path):
    from benedict import benedict

    cache = tmp_path / 'cache'
    params = benedict({'input_path': 's3://bucket/flight.fvc', 'cache_dir': cache})

    mock_s3 = MagicMock()
    with patch('boto3.client', return_value=mock_s3):
        result = dfu.input_path(params)

    assert result == cache / 'bucket' / 'flight.fvc'


def test_input_path_local_with_suffix(tmp_path):
    from benedict import benedict

    local = tmp_path / 'flight.nmea'
    local.write_text('data', encoding='utf-8')
    params = benedict({'input_path': str(local), 'suffix': '.fvc'})

    result = dfu.input_path(params)
    assert result == local.with_suffix('.fvc')


# --- fetch command -----------------------------------------------------------


def test_fetch_command(tmp_path):
    from click.testing import CliRunner
    from benedict import benedict

    from fvc.tools.df.cli import df

    cache = tmp_path / 'cache'
    mock_s3 = MagicMock()

    runner = CliRunner()
    with patch('boto3.client', return_value=mock_s3):
        result = runner.invoke(
            df,
            ['--cache-dir', str(cache), 'fetch', 's3://bucket/flight.fvc'],
            obj=benedict({'JSON': False, 'no_pprint': True}),
        )

    assert result.exit_code == 0, result.output
    expected = cache / 'bucket' / 'flight.fvc'
    mock_s3.download_file.assert_called_once_with('bucket', 'flight.fvc', str(expected))
