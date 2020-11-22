import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="file-caching", # Replace with your own username
    version="0.2",
    author="Olle Lindgren",
    author_email="lindgrenolle@live.se",
    description="A package for caching files locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OlleLindgren/file-caching",
    packages=setuptools.find_packages(),
    install_requires=[
          'pandas',
          'pyarrow',
          'termcolor'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)