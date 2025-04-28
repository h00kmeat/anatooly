import os
from collections import Counter, defaultdict
from typing import Dict, Tuple
from ..utils import read_files
from ..patterns import LANG_EXTENSIONS

class LanguageAnalyzer:
    def __init__(self, directory: str):
        self.directory = directory

    def detect_languages(self) -> Dict[str, float]:
        counter = Counter()
        total_files = 0

        for path, _ in read_files(self.directory):
            ext = os.path.splitext(path)[1].lower()
            filename = os.path.basename(path).lower()
            lang = "Other"

            for language, exts in LANG_EXTENSIONS.items():
                exts_lower = [e.lower() for e in exts]
                if ext in exts_lower or filename in exts_lower:
                    lang = language
                    break

            counter[lang] += 1
            total_files += 1

        distribution: Dict[str, float] = {}
        if total_files > 0:
            for lang, count in counter.items():
                distribution[lang] = count / total_files * 100.0
        return distribution

    def count_sloc(self) -> Tuple[Dict[str, int], int]:
        sloc_counter: Dict[str, int] = defaultdict(int)
        total_sloc = 0

        for path, content in read_files(self.directory):
            ext = os.path.splitext(path)[1].lower()
            filename = os.path.basename(path).lower()
            lang = "Other"

            for language, exts in LANG_EXTENSIONS.items():
                exts_lower = [e.lower() for e in exts]
                if ext in exts_lower or filename in exts_lower:
                    lang = language
                    break

            lines = sum(1 for line in content.splitlines() if line.strip())
            sloc_counter[lang] += lines
            total_sloc += lines

        return dict(sloc_counter), total_sloc
