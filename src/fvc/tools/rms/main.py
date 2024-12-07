''' Requirement Management System (RMS) tool. '''

from pathlib import Path
import tomllib
import logging as lg
from typing import cast
import json
import traceback

import click
from toolz.dicttoolz import valmap
from toolz.functoolz import compose
import pyparsing as pp
from git import Repo
from git.exc import GitCommandError

from fvc.tools.rms.model import load_model


class InputRecord:
    def __init__(self, input_class, record_base, filepaths, driver):
        self._input_class = input_class
        self._record_base = record_base
        self._filepaths = filepaths
        self._driver = driver


class Config:
    def __init__(self, params):
        self._input_records = []

        try:
            config_file = Path(params['config']).resolve()
            lg.debug(f'Using configuration file: {config_file}')
            self._base_dir = config_file.parent
            config = tomllib.loads(config_file.read_text())

            if params.get('verbose'):
                lg.debug(f'Configuration file content: {config}')

            if config.get('version') != 1:
                raise UserWarning('Unknown configuration file version (expected 1)')

            base = config.get('base')

            if not base:
                raise UserWarning('Missing base_dir parameter')

            input = config.get('input')

            if not input:
                raise UserWarning('Missing input section')

            for input_record in input:
                path = input_record.get('path')
                record_base = Path(base, path)

                if not path:
                    raise UserWarning('Missing input.path parameter')

                input_class = input_record.get('class')

                if not input_class:
                    raise UserWarning('Missing input.class parameter')

                driver = input_record.get('driver')

                if not driver:
                    raise UserWarning('Missing input.driver parameter')

                filter = input_record.get('filter')
                glob = filter or '**/*'

                if not filter and driver == 'obsidian':
                    lg.info(f'Using default filter (*.md) for {path}')
                    glob = '*.md'

                lg.debug(f'Adding input files from {path} with filter {glob}')
                filepaths = Path(base, Path(path)).glob(glob)

                self._input_records.append(InputRecord(
                    input_class, record_base, filepaths, driver
                ))

        except Exception as exc:
            lg.error(f'Error during configuration: {exc}')
            raise UserWarning('Bad configuration file')

        for input_record in self._input_records:
            print(input_record._record_base)
            print(list(input_record._filepaths))

    def base_dir(self):
        return self._base_dir

    def input_records(self):
        return self._input_records


class Item:
    all_uids = set()

    def __init__(self, uid: str, item_class: str, filename: Path, start_line: int):
        if not uid.startswith(item_class):
            raise UserWarning(f'UID {uid} does not start with class {item_class}')

        if uid in Item.all_uids:
            raise UserWarning(
                f'Duplicate UID: {uid} (file: {filename}, line: {start_line})')

        Item.all_uids.add(uid)

        self._uid = uid
        self._item_class = item_class
        self._filename = filename
        self._start_line = start_line
        self._end_line = None
        self._errors = []
        self._parents = []

    def set_end_line(self, line_no: int):
        self._end_line = line_no

    def set_version(self, version):
        self._version = version

    def uid(self):
        return self._uid

    def iclass(self):
        return self._item_class

    def __str__(self):
        return json.dumps(self.json(), indent=2)

    def json(self):
        return {
            'uid': self._uid,
            'class': self._item_class,
            'file': str(self._filename),
            'start': self._start_line,
            'stop': self._end_line,
            'version': self._version,
            'errors': self._errors
        }

    def begin(self):
        return self._start_line

    def end(self):
        assert self._end_line is not None
        return self._end_line

    def add_error(self, error):
        self._errors.append(error)

    def parents(self):
        return self._parents


class Extractor:
    def __init__(self, repo: Repo):
        self._repo = repo
        self._blame_lines = []
        self._items = []
        self._item = None
        self._file_name = None
        self._line_no = 0
        self._macro = []

    def grammar(self):
        return pp.And([
            pp.Suppress(pp.Literal('%[')),
            pp.Or([
                pp.Literal('<'),
                pp.Literal('>')
            ]),
            pp.Or([
                pp.Literal('REQ'),
                pp.Literal('SRC')
            ]),
            pp.Suppress(pp.Literal('.')),
            pp.Word(pp.alphanums + '.'),
            pp.Suppress(pp.Literal(']%'))
        ])

    def _report_malformed(self, macro=None):
        if not macro:
            macro = self._macro

        raise UserWarning(
            f'Malformed macro {macro} at line {self._line_no} in file {self._file_name}')

    def _report_mismatch_id(self):
        raise UserWarning(
            f'Mismatched UID at line {self._line_no} in file {self._file_name}')

    def _process_macro(self):
        command = self._macro[0]
        item_class = self._macro[1]
        uid = self._macro[2]

        if command == '<':
            if self._item is not None:
                self._report_malformed()

            lg.debug('Entering ITEM state')
            assert self._file_name is not None
            self._item = Item(uid, item_class, self._file_name, self._line_no)

        elif command == '>':
            if self._item is None:
                self._report_malformed()

            assert self._item is not None

            if self._item.uid() != uid or self._item._item_class != item_class:
                self._report_mismatch_id()

            lg.debug('Leaving ITEM state')
            item = self._item
            assert item is not None
            item.set_end_line(self._line_no)
            self._version_item(item)
            self._items.append(item)
            self._item = None

    def _version_item(self, item):
        start_inx = item.begin() - 1
        end_inx = item.end() - 1
        version = None

        for line in self._blame_lines[start_inx:end_inx]:
            current_version = line.split(' ')[0]
            lg.debug(f'Found version {item.uid()}@{current_version}')

            if self._is_ansestor(version, current_version):
                version = current_version
                lg.debug(f'Candidate version {item.uid()}@{version}')

        lg.debug(f'Final version {item.uid()}@{version}')
        assert version
        item.set_version(version)

    def _is_ansestor(self, version, current_version):
        if version is None:
            return True

        try:
            self._repo.git.execute([
                'git', 'merge-base', '--is-ancestor',
                version, current_version
            ])

            return True
        except GitCommandError:
            return False

    def _blame(self):
        lines = self._repo.git.execute([
            'git', 'blame', '-ls',
            '--', str(self._file_name)
        ])

        self._blame_lines = cast(str, lines).split('\n')

    def process_file(self, file_name: Path):
        self._file_name = file_name
        self._blame()
        self._line_no = 0
        text = file_name.read_text()

        for line in text.split('\n'):
            self._line_no += 1

            if line.find('%[') != -1:
                if match := self.grammar().searchString(line):
                    for macro in match:
                        lg.debug(f'Found macro: {macro}')
                        self._macro = macro
                        self._process_macro()
                else:
                    self._report_malformed([line])

    def items(self):
        return self._items


def build_deptree(items):
    deptree = {}

    for item in items.values():
        it = item.iclass()

        if it not in deptree:
            deptree[it] = {}

        deptree[it][item.uid()] = item

    return deptree


def treemap(func, deptree):
    return valmap(lambda i: valmap(func, i), deptree)


def validate(deptree):
    model = load_model()

    def validate_item(item):
        if item.iclass() not in model:
            item.add_error(f'Unknown class {item.iclass()}')
            return item

    def validate_root(item):
        if (class_def := model.get(item.iclass())) is None:
            return item

        if class_def.get('root') and len(item.parents()) > 0:
            item.add_error('Root item cannot have parents')

        return item

    validate = compose(
        validate_item,
        validate_root
    )

    treemap(validate, deptree)


@click.command(help='Requirement Management System (RMS) tool')
@click.pass_context
@click.option('--config', help='Configuration file', default='rms.toml')
def rms(ctx, config):
    ctx.obj['config'] = config
    config = Config(ctx.obj)

    items = {}

    repo = Repo(config.base_dir())
    return
    extractor = Extractor(repo)

    for file_name in config.input_file_names():
        lg.debug(f'Processing file: {file_name}')
        extractor.process_file(file_name)
        items.update({i.uid(): i for i in extractor.items()})

    deptree = build_deptree(items)
    validate(deptree)

    if ctx.obj['JSON']:
        jtree = treemap(lambda i: i.json(), deptree)
        print(json.dumps(jtree, indent=2))
