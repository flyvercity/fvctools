LOCATION = {
    'type': 'object',
    'properties': {
        'lat': {'type': 'number', '$comment': 'Latitude in WGS-84'},
        'lon': {'type': 'number', '$comment': 'Longitude in WGS-84'},
        'alt': {'type': 'number', '$comment': 'Ellipsoidal altitude'},
        'amsl': {'type': 'number', '$comment': 'Altitude above mean sea level'},
        'height': {'type': 'number', '$comment': 'Local height above ground'}
    },
    'required': ['lat', 'lon', 'alt'],
    'optional': ['alt', 'amsl', 'height']
}

POLAR = {
    'type': 'object',
    'properties': {
        'bear': {
            'type': 'number',
            '$comment': 'Bearing angle in degrees clockwise from the true north'
        },
        'elev': {
            'type': 'number',
            '$comment': 'Elevation angle in degrees above horizon'
        }
    }
}

POLAR_SENSOR = {
    'type': 'object',
    'properties': {
        'loc': LOCATION
    },
    'required': ['loc']
}

IDENTIFICATION = {
    'type': 'object',
    'properties': {
        'int': {'type': 'string', '$comment': 'Source-internal identifier'},
        'fvc': {'type': 'string', '$comment': 'Flyvercity unique identifier'},
        'icaohex': {'type': 'string', '$comment': 'ICAO 24-bit address'},
        'icaoreg': {'type': 'string', '$comment': 'ICAO registration'},
        'atm': {'type': 'string', '$comment': 'ATM callsign'},
    },
    'anyOf': [
        {'required': ['int']},
        {'required': ['fvc']}
    ]
}

CONTENT = {
    'type': 'string',
    'enum': [
        'flightlog',
        'radarlog',
        'fusion.replay'
    ],
    '$comment': 'Current file content descriptor'
}

METADATA = {
    'type': 'object',
    'properties': {
        'content': {
            'oneOf': [
                CONTENT,
                {
                    'type': 'array',
                    'items': CONTENT
                }
            ]
        },
        'source': {
            'type': 'string',
            'enum': [
                'airlink',
                'courageous',
                'csgroup',
                'nmea',
                'senhive',
                'robinradar',
                'safirmqtt',
                'fusion.replay',
                'artlog'
            ],
            '$comment': 'Original data format'
        },
        'origin': {'type': 'string', "$comment": "Original file name"},
        'polar_sensor': POLAR_SENSOR,
        'cycle_length': {'type': 'number'}
    },
    'required': ['content']
}

ATTITUDE = {
    'type': 'object',
    'properties': {
        'roll': {'type': 'number', '$comment': 'Roll angle in degrees'},
        'pitch': {'type': 'number', '$comment': 'Pitch angle in degrees'},
        'yaw': {'type': 'number', '$comment': 'Yaw angle in degrees'}
    },
    'required': ['roll', 'pitch', 'yaw']
}

POSITION = {
    'type': 'object',
    'properties': {
        'loc': LOCATION,
        'att': ATTITUDE
    },
    'required': ['loc'],
    'optional': ['att']
}

RADAR_POSITION = {
    'type': 'object',
    'properties': {
        'loc': POLAR
    },
    'required': ['loc'],
}

TIMESTAMP = {
    'type': 'object',
    'properties': {
        'unix': {'type': 'number', '$comment': 'Unix timestamp in milliseconds'},
    },
    'required': ['unix']
}


CELLULAR_SIGNAL = {
    'type': 'object',
    'properties': {
        'radio': {'type': 'string', 'enum': ['4G', '5Gd']},
        'RSRP': {'type': ['number', 'null']},
        'RSRQ': {'type': ['number', 'null']},
        'RSSI': {'type': ['number', 'null']},
        'SINR': {'type': ['number', 'null']}
    }
}

FLIGHTLOG = {
    'type': 'object',
    'properties': {
        'tag': {'type': 'string', 'enum': ['tgt'], '$comment': 'Geodetic target'},
        'origin': {'type': 'string'},
        'time': TIMESTAMP,
        'uaid': IDENTIFICATION,
        'pos': POSITION,
        'cellsig': CELLULAR_SIGNAL
    },
    'required': ['time', 'pos'],
    'optional': ['tag', 'uaid', 'origin', 'cellsig']
}

RADARLOG = {
    'type': 'object',
    'properties': {
        'tag': {'type': 'string', 'enum': ['ptgt'], '$comment': 'Polar target'},
        'origin': {'type': 'string'},
        'time': TIMESTAMP,
        'uaid': IDENTIFICATION,
        'pos': RADAR_POSITION
    },
    'required': ['time', 'pos'],
    'optional': ['tag', 'uaid', 'origin']
}

FUSION_REPLAY = {
    'type': 'object',
    'properties': {
        'event': {
            'type': 'string',
            'enum': [
                'launch',
                'start',
                'stop',
                'input',
                'output',
                'error'
            ]
        },
        'cycle': {'type': 'number'},
        'origin': {'type': 'string'},
        'message': {'type': 'object'},
        'eid': {'type': 'string'},
        'metadata': {'type': 'object'}
    },
    'required': ['event', 'cycle'],
    'optional': ['origin', 'message', 'eid', 'metadata']
}

CONTENT_SCHEMA = {
    'flightlog': FLIGHTLOG,
    'radarlog': RADARLOG,
    'fusion.replay': FUSION_REPLAY
}
