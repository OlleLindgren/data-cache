import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements=['pandas']

setuptools.setup(
    name="data-cache",
    version="v0.5",
    author="Olle Lindgren",
    author_email="lindgrenolle@live.se",
    description="A package for caching files locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OlleLindgren/data-cache",
    packages=setuptools.find_packages(),
    install_requires=["pandas"],
    extras_require={"way-faster-caching": ["pyarrow"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
