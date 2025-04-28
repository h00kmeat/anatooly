import os
from typing import Iterator, Tuple

def format_path(path: str, base_dir: str = None) -> str:
    if base_dir:
        try:
            rel = os.path.relpath(path, start=base_dir)
            return "/" + rel.replace("\\\\", "/")
        except ValueError:
            return path.replace("\\\\", "/")
    return path.replace("\\\\", "/")


def read_files(directory: str) -> Iterator[Tuple[str, str]]:
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                yield path, content
            except Exception:
                continue