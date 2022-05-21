"""Installer for the datacache package."""
import ast
from pathlib import Path

import setuptools

src_root = Path(__file__).parent

with open(src_root / "README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(src_root / "requirements.txt", "r", encoding="utf-8") as req_stream:
    requirements = [line.strip() for line in req_stream.readlines() if line.strip()]

with open(src_root / "datacache" / "__init__.py", "r", encoding="utf-8") as init_stream:
    version_line = next(line for line in init_stream.readlines() if "version" in line)
    version_string = version_line.split("=")[-1]
    version = ast.literal_eval(version_string.strip())

setuptools.setup(
    name="data-cache",
    version=version,
    author="Olle Lindgren",
    author_email="lindgrenolle@live.se",
    description="A package for caching files locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OlleLindgren/data-cache",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # Walrus :=, from __future__ import annotations
)
