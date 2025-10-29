import os
from pathlib import Path
import yaml

os.environ["LC_ALL"] = os.environ.get("LC_ALL", "C.UTF-8")

import jsonschema2md as js2md  # noqa: E402

schema = yaml.safe_load(Path('src/fvc/tools/df/schema.yaml').read_text())

metadata_schema = schema['METADATA']
flightlog_schema = schema['FLIGHTLOG']
radarlog_schema = schema['RADARLOG']
fusion_replay_schema = schema['FUSION_REPLAY']
capture_message_schema = schema['CAPTURE_MESSAGE']

parser = js2md.Parser(
    examples_as_yaml=False,
    show_examples='all'
)

metadata_md = ''.join(parser.parse_schema(metadata_schema))
flightlog_md = ''.join(parser.parse_schema(flightlog_schema))
radarlog_md = ''.join(parser.parse_schema(radarlog_schema))
fusion_replay_md = ''.join(parser.parse_schema(fusion_replay_schema))
capture_message_md = ''.join(parser.parse_schema(capture_message_schema))

schema_docs_dir = Path('docs/schema')
schema_docs_dir.mkdir(parents=True, exist_ok=True)
Path(schema_docs_dir / 'METADATA.md').write_text(metadata_md)
Path(schema_docs_dir / 'FLIGHTLOG.md').write_text(flightlog_md)
Path(schema_docs_dir / 'RADARLOG.md').write_text(radarlog_md)
Path(schema_docs_dir / 'FUSION_REPLAY.md').write_text(fusion_replay_md)
Path(schema_docs_dir / 'CAPTURE_MESSAGE.md').write_text(capture_message_md)

print(f'Schema documentation generated in {schema_docs_dir}')
