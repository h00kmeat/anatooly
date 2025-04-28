import os
from typing import Dict, List, Tuple
from .base import Detector
from ..patterns import CONFIG_PATTERNS, PASSWORD_PATTERN  

class ConfigDetector(Detector):
    def __init__(self, directory: str, config_patterns: Dict[str, Dict[str, str]] = None):
        super().__init__(directory)
        self.config_patterns = config_patterns or CONFIG_PATTERNS  
        self.detected: Dict[str, List[str]] = {}
        self.secrets: List[Tuple[str, List[str]]] = []

    def detect(self) -> Dict[str, List[str]]:
        for root, _, files in os.walk(self.directory):
            for cfg_file, tech_map in self.config_patterns.items():
                if cfg_file not in files:
                    continue
                path = os.path.join(root, cfg_file)
                try:
                    content = open(path, 'r', encoding='utf-8', errors='ignore').read()
                except Exception:
                    continue

                for pattern, tech in tech_map.items():
                    if pattern in content:
                        self.detected.setdefault(tech, []).append(path)
                secrets = PASSWORD_PATTERN.findall(content)
                if secrets:
                    values = [match[1] for match in secrets]
                    self.secrets.append((path, values))
        return self.detected

    def confidence(self) -> float:
        total_patterns = sum(len(p) for p in self.config_patterns.values())
        found = sum(len(paths) for paths in self.detected.values())
        return (found / total_patterns) if total_patterns else 0.0