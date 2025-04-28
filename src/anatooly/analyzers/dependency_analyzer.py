from collections import defaultdict
import os, json
from typing import Dict, Set, Union
from ..patterns import DEPENDENCY_PATTERNS, JS_TECH_DETECTION

class DependencyAnalyzer:
    def __init__(self, directory: str, main_lang: str):
        self.directory = directory
        self.main_lang = main_lang

    def analyze(self) -> Dict[str, Set[str]]:
        tech_stack: Dict[str, Set[str]] = defaultdict(set)
        for file_spec in DEPENDENCY_PATTERNS.get(self.main_lang, []):
            filename, patterns, category, *rest = (*file_spec, None)
            path = os.path.join(self.directory, filename)
            if not os.path.exists(path):
                continue
            if isinstance(patterns, dict):
                try:
                    data = json.load(open(path, 'r', encoding='utf-8', errors='ignore'))
                except Exception:
                    data = {}
                require = data.get('require', {})
                for pkg, tech in patterns.items():
                    if pkg in require:
                        tech_stack[category].add(tech)
            else:
                try:
                    text = open(path, 'r', encoding='utf-8', errors='ignore').read().lower()
                except Exception:
                    continue
                if patterns.lower() in text:
                    tech = rest[0] or patterns  
                    tech_stack[category].add(tech)
        pkg = None
        for root, _, files in os.walk(self.directory):
            if 'package.json' in files:
                pkg = os.path.join(root, 'package.json')
                break
        try:
            data = json.load(open(pkg, 'r', encoding='utf-8', errors='ignore')) if pkg else {}
        except Exception:
            data = {}
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            for tech, detector in JS_TECH_DETECTION.items():
                if any(pkg_name in deps for pkg_name in detector['packages']):
                    cat = detector['type']
                    tech_stack[cat].add(tech)

        return tech_stack