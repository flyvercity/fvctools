IDENTIFICATION = {
    'type': 'object',
    'properties': {
        'system': {
            'type': 'string',
            'enum': [
                'fvc',
                'internal',
                'icaohex'
            ]
        },
        'value': {'type': 'string'}
    }
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
                'bluehalo'
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
        'lat': {'type': 'number'},
        'lon': {'type': 'number'},
        'alt': {'type': 'number'}
    },
    'required': ['lat', 'lon', 'alt'],
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
        'unix': {'type': 'number'},
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
