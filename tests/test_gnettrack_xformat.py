import json
import pytest

from fvc.tools.df.utils import JsonlinesIO
from fvc.tools.df.xformats.gnettrack import convert_to_fvc


def test_convert_gnettrack_success(tmp_path):
    input_path = tmp_path / 'test_gnettrack.txt'
    input_path.write_text(
        "Timestamp\tDEVICE\tIP\tIMEI\tIMSI\tNetworkTech\tNetworkMode\tLevel\tQual\tLTERSSI\tSNR\tCSI_PCI\tCSI_RSRQ\tCSI_RSSI\tCSI_SNR\tSS_Level\tSS_Qual\tSS_RSSI\tSS_SNR\tARFCN\tBAND\tOperator\tOperatorname\tCGI\tLatitude\tLongitude\tAltitude\tPINGMAX\tPINGLOSS\tBATTERY\tAccuracy\tLocation\n"
        "2023.10.11_12.30.45.123\ttest-device\t192.168.1.1\t123456789012345\t987654321098765\t4G\tLTE\t-100\t-10\t-70\t15\t50\t-12\t-80\t12\t-105\t-15\t-85\t8\t1234\tB1\t20404\tTestOp\t204040123456789\t52.1234\t4.5678\t100.5\t50\t0\t80\t10\tGPS\n",
        encoding='utf-8',
    )

    output_path = tmp_path / 'out_gnettrack.fvc'

    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert len(rows) == 2
    assert rows[0]['content'] == 'flightlog'
    assert rows[0]['source'] == 'gnettrack'

    record = rows[1]
    assert 'unix' in record['time']
    assert record['time']['original'] == '2023.10.11_12.30.45.123'

    assert record['uaid']['ip'] == '192.168.1.1'
    assert record['uaid']['imei'] == '123456789012345'
    assert record['uaid']['imsi'] == '987654321098765'

    assert record['cellsig']['radio'] == '4GLTE'
    assert record['cellsig']['rsrp'] == -100.0

    assert record['pos']['loc'] == {
        'lat': 52.1234,
        'lon': 4.5678,
        'alt': 100.5,
    }

    assert record['datalink'] == {
        'rtt': 50,
        'loss': False,
    }

    assert record['metadata'] == {
        'BATTERY': '80',
        'Accuracy': '10',
        'Location': 'GPS',
    }


def test_convert_gnettrack_low_precision_failure(tmp_path):
    input_path = tmp_path / 'test_gnettrack_lp.txt'
    # Use low precision time (missing milliseconds)
    input_path.write_text(
        "Timestamp\tDEVICE\tIP\tIMEI\tIMSI\tNetworkTech\tNetworkMode\tLevel\tQual\tLTERSSI\tSNR\tCSI_PCI\tCSI_RSRQ\tCSI_RSSI\tCSI_SNR\tSS_Level\tSS_Qual\tSS_RSSI\tSS_SNR\tARFCN\tBAND\tOperator\tOperatorname\tCGI\tLatitude\tLongitude\tAltitude\tPINGMAX\tPINGLOSS\tBATTERY\tAccuracy\tLocation\n"
        "2023.10.11_12.30.45\ttest-device\t192.168.1.1\t123456789012345\t987654321098765\t4G\tLTE\t-100\t-10\t-70\t15\t50\t-12\t-80\t12\t-105\t-15\t-85\t8\t1234\tB1\t20404\tTestOp\t204040123456789\t52.1234\t4.5678\t100.5\t50\t0\t80\t10\tGPS\n",
        encoding='utf-8',
    )

    output_path = tmp_path / 'out_gnettrack_lp.fvc'

    with pytest.raises(UserWarning) as excinfo:
        with JsonlinesIO(output_path, 'w') as output:
            convert_to_fvc({}, {'origin': 'unit-test'}, input_path, output)

    assert 'Invalid time setting' in str(excinfo.value)


def test_convert_gnettrack_low_precision_allowed(tmp_path):
    input_path = tmp_path / 'test_gnettrack_lp_allowed.txt'
    # Use low precision time (missing milliseconds)
    input_path.write_text(
        "Timestamp\tDEVICE\tIP\tIMEI\tIMSI\tNetworkTech\tNetworkMode\tLevel\tQual\tLTERSSI\tSNR\tCSI_PCI\tCSI_RSRQ\tCSI_RSSI\tCSI_SNR\tSS_Level\tSS_Qual\tSS_RSSI\tSS_SNR\tARFCN\tBAND\tOperator\tOperatorname\tCGI\tLatitude\tLongitude\tAltitude\tPINGMAX\tPINGLOSS\tBATTERY\tAccuracy\tLocation\n"
        "2023.10.11_12.30.45\ttest-device\t192.168.1.1\t123456789012345\t987654321098765\t4G\tLTE\t-100\t-10\t-70\t15\t50\t-12\t-80\t12\t-105\t-15\t-85\t8\t1234\tB1\t20404\tTestOp\t204040123456789\t52.1234\t4.5678\t100.5\t50\t0\t80\t10\tGPS\n",
        encoding='utf-8',
    )

    output_path = tmp_path / 'out_gnettrack_lp_allowed.fvc'

    params = {'custom': ['gnettrack-allow-low-precision']}
    with JsonlinesIO(output_path, 'w') as output:
        convert_to_fvc(params, {'origin': 'unit-test'}, input_path, output)

    rows = [json.loads(line) for line in output_path.read_text(encoding='utf-8').splitlines()]

    assert len(rows) == 2
    assert rows[1]['metadata'].get('low_precision') is True
