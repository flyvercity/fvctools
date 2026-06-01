from unittest.mock import patch

from fvc.tools.df.xformats.nmea import iterate_nmea_file


def test_iterate_nmea_file_empty_message_types_skips_all(tmp_path):
    input_path = tmp_path / 'test.nmea'
    input_path.write_text('$GPGGA,foo*00\n', encoding='utf-8')

    with patch('fvc.tools.df.xformats.nmea.pynmea2.parse') as mock_parse:
        assert list(iterate_nmea_file(input_path, message_types=[])) == []
        mock_parse.assert_not_called()


def test_iterate_nmea_file_filters_on_header_only(tmp_path):
    input_path = tmp_path / 'test.nmea'
    input_path.write_text('$GPRMC,contains-GGA*00\n', encoding='utf-8')

    with patch('fvc.tools.df.xformats.nmea.pynmea2.parse') as mock_parse:
        assert list(iterate_nmea_file(input_path, message_types=['GGA'])) == []
        mock_parse.assert_not_called()
