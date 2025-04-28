import os, re
from typing import List, Dict, Any
from .base import Detector
from ..patterns import HEADER_PATTERNS, ENDPOINT_IGNORE_FILE_PATTERNS

class HeaderDetector(Detector):
    def __init__(self, directory: str, langs: List[str]):
        super().__init__(directory)
        self.langs = langs

    def detect(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        for root, _, files in os.walk(self.directory):
            for fname in files:
                fpath = os.path.join(root, fname)
                if any(pat.search(fpath) for pat in ENDPOINT_IGNORE_FILE_PATTERNS):
                    continue

                ext = os.path.splitext(fname)[1].lower()
                lang = {'.js':'JavaScript', '.py':'Python', '.go':'Go', '.java':'Java'}.get(ext)
                if lang not in self.langs:
                    continue

                fpath = os.path.join(root, fname)
                try:
                    text = open(fpath, encoding='utf-8', errors='ignore').read()
                except:
                    continue
                rel = os.path.relpath(fpath, self.directory)

                for regex, framework in HEADER_PATTERNS.get(lang, []):
                    for m in regex.finditer(text):
                        gd = m.groupdict()
                        ln = text[:m.start()].count('\n') + 1
                        hdrs = gd.get('headers')
                        if not hdrs and gd.get('headerName'):
                            hdrs = {gd['headerName']: gd.get('headerValue')}
                        if isinstance(hdrs, dict):
                            hdrs = {k.lower(): v for k, v in hdrs.items()}

                        results.append({
                            'file':      rel,
                            'line':      ln,
                            'framework': framework,
                            'method':    gd.get('method'),
                            'endpoint':  gd.get('url'),
                            'headers':   hdrs,
                        })

        return results

    def confidence(self) -> float:
        return 1.0 if self.detect() else 0.0
