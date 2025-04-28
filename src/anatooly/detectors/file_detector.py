import os
import glob
from typing import List, Dict, Any, Tuple
from .base import Detector

class FileDetector(Detector):
    def __init__(self, directory: str, configs: List[Dict[str, Any]]):
        super().__init__(directory)
        self.configs = configs
        self._matches: List[Tuple[str, Any]] = []

    def detect(self) -> Tuple[bool, List[Tuple[str, Any]]]:
        self._matches.clear()
    
        for cfg in self.configs:
            expected_type = cfg.get('type', 'file')
            if isinstance(cfg.get('pattern'), re.Pattern):
                pat: re.Pattern = cfg['pattern']
                for root, _, files in os.walk(self.directory):
                    for fname in files:
                        if pat.search(fname):
                            full = os.path.join(root, fname)
                            if expected_type == 'dir' and os.path.isdir(full):
                                self._matches.append((full, None))
                            elif expected_type == 'file' and os.path.isfile(full):
                                if 'content' in cfg:
                                    text = open(full, 'r', encoding='utf-8', errors='ignore').read()
                                    if cfg['content'] in text:
                                        self._matches.append((full, cfg['content']))
                                else:
                                    self._matches.append((full, None))
                continue

            pattern_str = cfg.get('path', '')
            for full in glob.glob(os.path.join(self.directory, pattern_str), recursive=True):
                if expected_type == 'dir' and os.path.isdir(full):
                    self._matches.append((full, None))
                elif expected_type == 'file' and os.path.isfile(full):
                    if 'content' in cfg:
                        text = open(full, 'r', encoding='utf-8', errors='ignore').read()
                        if cfg['content'] in text:
                            self._matches.append((full, cfg['content']))
                    else:
                        self._matches.append((full, None))
    
        return (bool(self._matches), self._matches)

    def confidence(self) -> float:
        total = len(self.configs)
        return (len(self._matches) / total) if total > 0 else 0.0