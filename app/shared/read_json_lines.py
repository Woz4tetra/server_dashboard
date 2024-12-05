import json
from typing import Generator


def read_json_lines(reader) -> Generator[dict, None, None]:
    for line in reader.readlines():
        try:
            yield json.loads(line)
        except BaseException as e:
            print(f"Error reading line: {e}")
            continue
