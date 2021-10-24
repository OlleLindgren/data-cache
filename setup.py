import setuptools
from pathlib import Path

src_root = Path(__file__).parent

with open(src_root / "README.md", "r") as fh:
    long_description = fh.read()

with open(src_root / 'requirements.txt', 'r') as f:
    requirements = [r.strip() for r in f.readlines() if r.strip()]

with open(src_root / '__init__.py', "r") as f:
    __version_line = next(filter(lambda s: 'version' in s, f.readlines()))
    version = __version_line.split('=')[-1].strip(" \n\"")

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
    python_requires='>=3.6',
)
