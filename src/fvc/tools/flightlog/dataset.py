from benedict import benedict
import polars as pl


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
