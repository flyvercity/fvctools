import jsonschema


def schema():
    return {
        'type': 'object',
        "patternProperties": {
            "^[A-Z]+$": {
                'type': 'object',
                'properties': {
                    'root': {'type': 'boolean'},
                    'children': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    }
                },
                'required': ['root'],
                'additionalProperties': False
            }
        }
    }


def default_model():
    return {
        'REQ': {
            'root': True
        }
    }


def load_model():
    model = default_model()
    jsonschema.validate(model, schema())
    return model
