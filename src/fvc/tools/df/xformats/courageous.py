import json
from pathlib import Path
import logging as lg

import fvc.tools.util as u
from fvc.tools.df.util import JsonlinesIO


class Courageous:
    def __init__(self, params, metadata, input_path: Path, output: JsonlinesIO):
        self.params = params
        self.metadata = metadata
        self.input_path = input_path
        self.output = output
        self.geoid = u.load_geoid(self.params, self.metadata)

    def build_position(self, loc):
        pass

    def content(self):
        pass

    def convert(self):
        self.metadata.update({'content': self.content(), 'source': 'courageous'})
        self.output.write(self.metadata)
        data = json.loads(self.input_path.read_text())

        entries = []

        for track in data.get('tracks', []):
            track_name = track.get('name', 'unknown')
            track_id = track.get('uas_id', 'noid')

            uaid = {
                'int': f'{track_name}-{track_id}',
            }

            def record_to_entry(record):
                timestamp = {'unix': record['time']}
                flog_record = {'time': timestamp, 'uaid': uaid}
                position = self.build_position(record['location'])
                
                if position:
                    flog_record.update({'pos': position})

                return flog_record

            entries.extend(map(record_to_entry, track['records']))

        entries.sort(key=lambda e: e['time']['unix'])

        for entry in entries:
            self.output.write(entry)


class CourageousCartesian(Courageous):
    def content(self):
        return 'flightlog'

    def build_position(self, loc):
        if 't' in loc and loc['t'] == 'Position3d':
            pos = loc['c']
        elif 'Position3d' in loc:
            pos = loc['Position3d']
        else:
            lg.warning(f'Unused location format: {loc.get("t")}')
            return None

        lat = pos['lat']
        lon = pos['lon']
        amsl = pos['height_amsl']
        alt = u.amsl_to_ellipsoidal(self.geoid, lat, lon, amsl)

        position = {
            'loc': {
                'lat': lat,
                'lon': lon,
                'alt': alt
            }
        }

        return position


class CourageousPolar(Courageous):
    def content(self):
        return 'radarlog'

    def build_position(self, loc):
        if loc.get('t') == 'BearingElevation':
            pos = loc['c']
        else:
            lg.warning(f'Unused location format: {loc.get("t")}')
            return None

        position = {
            'loc': {
                'polar': {
                    'bear': pos['bearing'],
                    'elev': pos['elevation']
                }
            }
        }

        return position


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    if params.get('target') == 'flightlog':
        Converter = CourageousCartesian
    elif params.get('target') == 'radarlog':
        Converter = CourageousPolar
    else:
        raise ValueError(f'Unsupported content type: {params.get("content")}')
    
    Converter(params, metadata, input_path, output).convert()
