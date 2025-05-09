# ~/.vi/src/setup.py

from setuptools import setup, find_packages

setup(
    name="vi",
    version="0.1",
    packages=find_packages(include=['vi', 'vi.*', 'models', 'models.*']),
)