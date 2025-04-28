"""Компоненты-аналитики, которые обёртывают детекторы и собирают результаты"""
from .language_analyzer import LanguageAnalyzer
from .stack_analyzer import StackAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .secret_analyzer import SecretAnalyzer
from .report_generator import ReportGenerator

__all__ = [
    "LanguageAnalyzer",
    "StackAnalyzer",
    "DependencyAnalyzer",
    "SecretAnalyzer",
    "ReportGenerator",
]