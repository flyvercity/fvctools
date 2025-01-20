
from pathlib import Path
import csv

from fvc.tools.df.util import JsonlinesIO


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    with input_path.open('rt') as input:
        reader = csv.DictReader(input)

        for row in reader:
            print(row)

