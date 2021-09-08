import setuptools
from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(Path(__file__).parent/'requirements.txt', 'r') as f:
    requirements = [r.strip() for r in f.readlines() if r.strip()]

setuptools.setup(
    name="data-cache",
    version="v0.7.6",
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
    python_requires='>=3.6',
)
