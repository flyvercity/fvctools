METADATA = {
    'type': 'object',
    'properties': {
        'content': {
            'type': 'string',
            'enum': ['flightlog']
        },
        'source': {
            'type': 'string',
            'enum': ['airlink']
        },
        'origin': {'type': 'string'}
    },
    'additionalProperties': True
}

LOCATION = {
    'type': 'object',
    'properties': {
        'lat': {'type': 'number'},
        'lon': {'type': 'number'},
        'alt': {'type': 'number'}
    },
    'required': ['lat', 'lon', 'alt']
}


POSITION = {
    'type': 'object',
    'properties': {
        'location': LOCATION
    },
    'additionalProperties': True
}

TIMESTAMP = {
    'type': 'object',
    'properties': {
        'unix': {'type': 'number'},
    },
    'additionalProperties': False
}

FLIGHTLOG = {
    'type': 'object',
    'properties': {
        'timestamp': TIMESTAMP,
        'position': POSITION
    },
    'additionalProperties': True

}

CONTENT_SCHEMA = {
    'flightlog': FLIGHTLOG
}
