from benedict import benedict
import polars as pl
from fvc.tools.utils import plnested
import fvc.tools.df.utils as dfu
from pathlib import Path


class FlightlogDataset:
    metadata: benedict
    frames: list[pl.DataFrame]

    def __init__(self, *, metadata: benedict, frames: list[pl.DataFrame]):
        self.metadata = metadata
        self.frames = frames

    def serialize(self) -> dict:
        return {
            'metadata': self.metadata.dict(),
            'frames': [frame.to_dicts() for frame in self.frames],
        }

    @staticmethod
    def deserialize(data: dict) -> 'FlightlogDataset':
        return FlightlogDataset(
            metadata=benedict(data['metadata']),
            frames=[pl.DataFrame(frame) for frame in data['frames']],
        )

    def evolve(
        self, *,
        frames: list[pl.DataFrame],
        metadata: benedict | dict = {}
    ) -> 'FlightlogDataset':
        new_metadata = benedict(metadata)
        new_metadata['upstream'] = self.metadata

        return FlightlogDataset(
            metadata=new_metadata,
            frames=frames,
        )


def load_frame(input_path: Path):
    """ Parameters:
        - input_path: Path to the FVC data file
    """
    dataset = dfu.FvcDataset.read(input_path)

    if dataset.metadata.get('content') != 'flightlog':
        raise UserWarning(f'File {input_path} is not a flightlog')

    df = dataset.df

    df = df.with_columns(
        plnested('time.unix').alias('timestamp'),
    )

    return FlightlogDataset(
        metadata=dataset.metadata,
        frames=[df.sort('timestamp')],
    )
