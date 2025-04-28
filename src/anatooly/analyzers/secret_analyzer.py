from typing import List, Tuple
import fnmatch
from ..patterns import PASSWORD_PATTERN

class SecretAnalyzer:
    def __init__(self, directory: str):
        self.directory = directory

    def find_secrets(self) -> List[Tuple[str, List[str]]]:
        pass
