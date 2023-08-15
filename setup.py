from setuptools import setup, find_packages

from HDrezka import __version__

with open('README.md', encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name="HDrezka",
    version=__version__.__version__,
    packages=find_packages(),
    long_description=readme,

)
