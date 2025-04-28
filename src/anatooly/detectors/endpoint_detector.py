import os
import re
from typing import List, Dict, Any
from .base import Detector
from ..patterns import (
    ENDPOINT_PATTERNS,
    AJAX_PATTERN_EXT,
    ENDPOINT_IGNORE_FILE_PATTERNS
)

EXTENSION_LANG_MAP = {
    '.js':   'JavaScript',
    '.jsx':  'JavaScript',
    '.ts':   'TypeScript',
    '.tsx':  'TypeScript',
    '.py':   'Python',
    '.rb':   'Ruby',
    '.php':  'PHP',
    '.go':   'Go',
    '.java': 'Java',
    '.kt':   'Kotlin',
}

class EndpointDetector(Detector):
    def __init__(self, directory: str, langs: List[str]):
        super().__init__(directory)
        self.langs = langs

    def detect(self) -> Dict[str, List[Dict[str, Any]]]:
        
        records: List[tuple] = []
        ajax_calls = set()

        for root, _, files in os.walk(self.directory):
            for fname in files:
                fpath = os.path.join(root, fname)

                if any(pat.search(fpath) for pat in ENDPOINT_IGNORE_FILE_PATTERNS):
                    continue

            
                ext = os.path.splitext(fname)[1].lower()
                if ext not in EXTENSION_LANG_MAP:
                    continue

                try:
                    text = open(fpath, 'r', encoding='utf-8', errors='ignore').read()
                except Exception:
                    continue

                rel = os.path.relpath(fpath, start=self.directory)

                lang_for_file = EXTENSION_LANG_MAP[ext]
                if lang_for_file not in self.langs:
                    continue

                for regex, framework in ENDPOINT_PATTERNS.get(lang_for_file, []):
                    for m in regex.finditer(text):
                        if regex.groups >= 2:
                            ann = m.group(1)
                            if framework == "Spring MVC":
                                ann_lower = ann.lower()
                                if ann_lower.endswith("mapping"):
                                    method = ann_lower[:-7].upper()  
                                else:
                                    method = "ALL"
                            else:
                                method = ann.upper()
                            route = m.group(2)
                        else:
                            method = "ALL"
                            route = m.group(1)

                        line_no = text[:m.start()].count('\n') + 1
                        records.append((rel, line_no, framework, method, route))

                for match in AJAX_PATTERN_EXT.finditer(text):
                    url = next((g for g in match.groups() if g), None)
                    if not url:
                        continue
                    line_no = text[:match.start()].count('\n') + 1
                    ajax_calls.add((rel, line_no, url))

        records.sort(key=lambda x: (x[0], x[1]))
        endpoint_list: List[Dict[str, Any]] = [
            {'file': f, 'line': ln, 'framework': fw, 'method': meth, 'endpoint': ep}
            for f, ln, fw, meth, ep in records
        ]
        ajax_list = [
            {'file': fp, 'line': ln, 'call': url}
            for fp, ln, url in sorted(ajax_calls)
        ]

        return {'endpoints': endpoint_list, 'ajax': ajax_list}

    def confidence(self) -> float:
        res = self.detect()
        return 1.0 if (res['endpoints'] or res['ajax']) else 0.0
