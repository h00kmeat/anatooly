"""Набор детекторов для анализа кода"""
from .base import Detector
from .file_detector import FileDetector
from .code_detector import CodeDetector
from .config_detector import ConfigDetector
from .endpoint_detector import EndpointDetector

__all__ = [
    "Detector",
    "FileDetector",
    "CodeDetector",
    "ConfigDetector",
    "EndpointDetector",
]