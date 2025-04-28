import os
import re
from typing import List, Tuple
from .base import Detector

class CodeDetector(Detector):
    def __init__(self, directory: str, pattern: str):
        super().__init__(directory)
        if isinstance(pattern, re.Pattern):
            self.pattern = pattern
        else:
            self.pattern = re.compile(pattern, re.IGNORECASE)
        self._matches: List[Tuple[str, int, str]] = []

    def detect(self) -> List[Tuple[str, int, str]]:
        self._matches.clear()
        for root, _, files in os.walk(self.directory):
            for fname in files:
                if not fname.endswith(('.py', '.js', '.ts', '.java', '.php', '.cs', '.json')):
                    continue
                path = os.path.join(root, fname)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for lineno, line in enumerate(f, start=1):
                            m = self.pattern.search(line)
                            if m:
                                self._matches.append((path, lineno, m.group(0)))
                except Exception:
                    continue
        return self._matches

    def confidence(self) -> float:
        total = 0
        seen_files = set(path for path, _, _ in self._matches)
        for root, _, files in os.walk(self.directory):
            for fname in files:
                if fname.endswith(('.py', '.js', '.ts', '.java', '.php', '.cs','json')):
                    total += 1
        return (len(seen_files) / total) if total > 0 else 0.0