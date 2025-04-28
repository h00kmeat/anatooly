"""
Code Analyzer — инструмент для анализа безопасности исходного кода
"""
__version__ = "0.1.0"

# чтобы можно было делать:
#   import code_analyzer
#   code_analyzer.main(...)
from .cli import main