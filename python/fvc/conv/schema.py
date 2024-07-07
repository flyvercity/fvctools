IDENTIFICATION = {
    'type': 'object',
    'properties': {
        'int': {'type': 'string'},
        'fvc': {'type': 'string'},
        'icaohex': {'type': 'string'}
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
            'enum': ['flightlog']
        },
        'source': {
            'type': 'string',
            'enum': [
                'airlink',
                'bluehalo',
                'csgroup'
            ]
        },
        'origin': {'type': 'string'}
    },
    'required': ['content'],
    'additionalProperties': True
}

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
    'optional': ['amsl', 'height'],
    'additionalProperties': True
}


POSITION = {
    'type': 'object',
    'properties': {
        'loc': LOCATION
    },
    'required': ['loc'],
    'additionalProperties': True
}

TIMESTAMP = {
    'type': 'object',
    'properties': {
        'unix': {'type': 'number', '$comment': 'Unix timestamp in milliseconds'},
    },
    'required': ['unix'],
    'additionalProperties': True
}

FLIGHTLOG = {
    'type': 'object',
    'properties': {
        'time': TIMESTAMP,
        'uaid': IDENTIFICATION,
        'pos': POSITION
    },
    'required': ['time', 'pos'],
    'optional': ['uaid'],
    'additionalProperties': True
}

CONTENT_SCHEMA = {
    'flightlog': FLIGHTLOG
}
