from pathlib import Path
from xml.parsers.expat import ParserCreate
from typing import TextIO, Any
import logging as lg

import fvc.tools.df.util as u


def iterate_robin(f: TextIO):
    line_no = 0

    while True:
        line = f.readline()
        line_no += 1

        if not line:
            return

        if '<Robin>' in line:
            lines = [line]

            while '</Robin>' not in line:
                if line := f.readline():
                    line_no += 1
                    lines.append(line)
                else:
                    return
            
            yield (line_no, ''.join(lines))


class Context:
    def __init__(self, output: u.JsonlinesIO):
        self.output = output


class Converter:
    class Top:
        pass

    class Dummy():
        def __init__(self, parent):
            self.parent = parent

    class Track:
        def __init__(self, ctx, parent, attrs):
            self.ctx = ctx
            self.parent = parent
            self.record = {'uid': {'int': attrs['id']}}

        def close(self):
            self.ctx.output.write(self.record)

    class Timestamp:
        def __init__(self, ctx, parent, attrs):
            self.ctx = ctx
            self.parent = parent
            self.time = None

        def cdata(self, data):
            self.time = u.datestring_to_ts(data)

        def close(self):
            if self.time is None:
                raise ValueError('Incomplete timestamp record')

            if type(self.parent) is Converter.Track:
                self.parent.record['time'] = {'unix': self.time}

    class Position:
        def __init__(self, ctx, parent, attrs):
            self.ctx = ctx
            self.parent = parent
            self.lat = None  # type: float | None
            self.lon = None  # type: float | None
            self.alt = None  # type: float | None

        def close(self):
            if self.lat is None or self.lon is None or self.alt is None:
                raise ValueError('Incomplete position record') 

            if type(self.parent) is Converter.Track:
                self.parent.record['pos'] = {
                    'loc': {
                        'lat': self.lat,
                        'lon': self.lon,
                        'alt': self.alt
                    }
                }

    class Latitude:
        def __init__(self, ctx, parent, attrs):
            self.ctx = ctx
            self.parent = parent
            self.lat = None  # type: float | None

        def cdata(self, data):
            self.lat = float(data)

        def close(self):
            if self.lat is None:
                raise ValueError('Incomplete latitude record')

            if type(self.parent) is Converter.Position:
                self.parent.lat = self.lat

    class Longitude:
        def __init__(self, ctx, parent, attrs):
            self.ctx = ctx
            self.parent = parent
            self.lon = None

        def cdata(self, data):
            self.lon = float(data)

        def close(self):
            if self.lon is None:
                raise ValueError('Incomplete longitude record')

            if type(self.parent) is Converter.Position:
                self.parent.lon = self.lon

    class Altitude:
        def __init__(self, ctx, parent, attrs):
            self.ctx = ctx
            self.parent = parent
            self.alt = None

        def cdata(self, data):
            self.alt = float(data)

        def close(self):
            if self.alt is None:
                raise ValueError('Incomplete altitude record')

            if type(self.parent) is Converter.Position:
                self.parent.alt = self.alt


    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.current = Converter.Top()  # type: Any

    def start_element(self, name, attrs):
        Class = getattr(Converter, name, None)

        if Class:
            element = Class(self.ctx, self.current, attrs)
        else:
            element = Converter.Dummy(self.current)

        self.current = element

    def cdata(self, data):
        if cdata_method := getattr(self.current, 'cdata', None):
            cdata_method(data)

    def end_element(self, name):
        if close_method := getattr(self.current, 'close', None):
            close_method()

        self.current = self.current.parent


def convert_to_fvc(params, metadata, input_path: Path, output: u.JsonlinesIO):
    metadata.update({'content': 'flightlog', 'source': 'robinradar'})
    output.write(metadata)
    ctx = Context(output)

    with input_path.open('rt') as f:
        block_no = 0

        for (line_no, block) in iterate_robin(f):
            block_no += 1

            try:
                parser = ParserCreate()
                converter = Converter(ctx)
                parser.StartElementHandler = converter.start_element
                parser.CharacterDataHandler = converter.cdata
                parser.EndElementHandler = converter.end_element
                parser.Parse(block, True)
            
            except Exception as e:
                lg.warning(f'Error parsing block {block_no} line {line_no}: {e}')
