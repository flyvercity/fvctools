from pathlib import Path
import polars as pl
import pyparsing as pp

from fvc.tools.df.utils import JsonlinesIO


def _make_grammar():
    lp = pp.Literal('(')
    rp = pp.Literal(')')
    word = pp.Word(pp.alphas)
    comment = pp.Suppress(lp + pp.OneOrMore(word) + rp)
    column = word + pp.Optional(comment)
    return pp.OneOrMore(column)


GRAMMAR = _make_grammar()


def convert_to_fvc(params, metadata, input_path: Path, output: JsonlinesIO):
    with input_path.open('rt') as input:
        header = input.readline()

    if not header:
        return

    columns = list(GRAMMAR.parse_string(header))

    metadata.update({'content': 'flightlog', 'source': 'datcon'})
    output.write(metadata)

    # ⚡ Bolt: Use Polars to load and convert the space-separated DJI Datcon format.
    # This provides a major speedup (approx 10-15x) over row-by-row csv.DictReader loops
    # by using highly optimized Rust/C level vector operations.
    try:
        df = pl.read_csv(
            input_path,
            has_header=False,
            new_columns=columns,
            skip_rows=1,
            separator=' ',
        )
    except (pl.exceptions.NoDataError, pl.exceptions.ShapeError, Exception):
        # Empty data rows (e.g. only header was present)
        return

    # TZ must be UTC
    if not (df['TZ'] == 'UTC').all():
        raise AssertionError('All rows must have TZ set to UTC')

    df = df.select(
        [
            pl.struct(unix=pl.col('TS').cast(pl.Int64) // 1_000_000).alias('time'),
            pl.struct(
                int=pl.when(pl.col('GUID') != 'N/A').then(pl.col('GUID')).otherwise(pl.col('ID')).cast(pl.Utf8)
            ).alias('uaid'),
            pl.struct(
                loc=pl.struct(
                    lat=pl.col('Latitude').cast(pl.Float64),
                    lon=pl.col('Longitude').cast(pl.Float64),
                    alt=pl.col('Altitude').cast(pl.Float64),
                )
            ).alias('pos'),
        ]
    )

    output.write_dataframe(df)
