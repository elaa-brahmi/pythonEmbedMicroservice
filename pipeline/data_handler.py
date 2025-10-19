import os
from typing import Iterable

try:
    import ijson
except ImportError:
    ijson = None


def stream_data(file_path: str) -> Iterable[dict]:
    print(f"stream_data: opening file {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    if ijson is None:
        raise RuntimeError(
            "ijson is required for streaming large JSON arrays. "
            "Install with `pip install ijson`."
        )

    with open(file_path, "r", encoding="utf-8") as f:
        print(f"stream_data: using ijson to parse JSON array from {file_path}")
        try:
            for obj in ijson.items(f, "item"):
                yield obj
        except Exception as e:
            raise RuntimeError(f"Failed to stream JSON data: {e}")
