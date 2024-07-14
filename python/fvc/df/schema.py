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
    'optional': ['amsl', 'height']
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
        'int': {'type': 'string'},
        'fvc': {'type': 'string'},
        'icaohex': {'type': 'string'},
        'icaoreg': {'type': 'string'},
        'atm': {'type': 'string'}
    },
    'anyOf': [
        {'required': ['int']},
        {'required': ['fvc']}
    ]
}

METADATA = {
    'type': 'object',
    'properties': {
        'content': {
            'type': 'string',
            'enum': [
                'flightlog',
                'radarlog',
                'fusion.replay'
            ],
            '$comment': 'Current file content descriptor'
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
                'fusion.replay'
            ],
            '$comment': 'Original data format'
        },
        'origin': {'type': 'string', "$comment": "Original file name"},
        'polar_sensor': POLAR_SENSOR,
        'cycle_length': {'type': 'number'}
    },
    'required': ['content']
}

POSITION = {
    'type': 'object',
    'properties': {
        'loc': LOCATION
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

FLIGHTLOG = {
    'type': 'object',
    'properties': {
        'tag': {'type': 'string', 'enum': ['tgt'], '$comment': 'Geodetic target'},
        'origin': {'type': 'string'},
        'time': TIMESTAMP,
        'uaid': IDENTIFICATION,
        'pos': POSITION
    },
    'required': ['time', 'pos'],
    'optional': ['tag', 'uaid', 'origin']
}

RADARLOG = {
    'type': 'object',
    'properties': {
        'tag': {'type': 'string', 'enum': ['ptgt'], '$comment': 'Polar target'},
        'origin': {'type': 'string'},
        'time': TIMESTAMP,
        'uaid': IDENTIFICATION,
        'pos': POSITION
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
    'fusion.replay': FUSION_REPLAY
}
