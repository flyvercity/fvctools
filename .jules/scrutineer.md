The project includes wrapper functions for pathlib operations like 'stat_size' which are unnecessary since callers can (and often do) use 'input_path.stat().st_size' directly. They should be removed.
