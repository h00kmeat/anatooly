from typing import Dict, Set
import os
import re
from ..patterns import TECHNOLOGY_DETECTORS, TECHNOLOGIES_BY_LANG, JS_TECH_DETECTION
from ..detectors.file_detector import FileDetector
from ..detectors.code_detector import CodeDetector

class StackAnalyzer:
    def __init__(self, directory: str, main_lang: str):
        self.directory = directory
        self.main_lang = main_lang
        self.detectors = []

    def prepare_detectors(self):
        pkg_json_path = os.path.join(self.directory, "package.json")
        if os.path.isfile(pkg_json_path):
            for root, _, files in os.walk(self.directory):
                if 'package.json' in files:
                    pkg_json_path = os.path.join(root, 'package.json')
                    break
        if pkg_json_path:
            for tech, info in JS_TECH_DETECTION.items():
                cat = {"frontend":"frontend","backend":"backend"}.get(info["type"], "database")
                cfg = {
                    "type":    "file",
                    "path":    os.path.relpath(pkg_json_path, self.directory),
                    "content": r"['\"](?:%s)['\"]" % "|".join(info["packages"])
                }
                self.detectors.append((cat, tech, [FileDetector(self.directory, [cfg])]))

        for category_key, tech_list in TECHNOLOGIES_BY_LANG.get(self.main_lang, {})\
                                        .items():
            for tech in tech_list:
                configs = TECHNOLOGY_DETECTORS.get(tech, [])
                instances = []
                for cfg in configs:
                    t = cfg.get("type")
                    if t in ("file", "dir"):
                        instances.append(FileDetector(self.directory, [cfg]))
                    elif t == "code":
                        instances.append(CodeDetector(self.directory, cfg["pattern"]))
                if instances:
                    self.detectors.append((category_key, tech, instances))

    def analyze_stack(self) -> Dict[str, Set[str]]:
        result = {
            "backend":     set(),
            "frontend":    set(),
            "database":    set(),
            "build_tools": set(),
            "testing":     set(),
            "devops":      set(),
        }
        category_map = {
            "frameworks":      "backend",
            "frontend":        "frontend",
            "databases":       "database",
            "build_tools":     "build_tools",
            "test_frameworks": "testing",
            "devops":          "devops",
        }

        for category_key, tech, instances in self.detectors:
            mapped = category_map.get(category_key, category_key)
            for det in instances:
                try:
                    detected = det.detect()
                except Exception:
                    continue
                found = detected[0] if isinstance(detected, tuple) else bool(detected)
                if found:
                    result[mapped].add(tech)
                    break
        return result