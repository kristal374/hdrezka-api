from setuptools import setup, find_packages
import HDrezka

with open('README.md') as readme_file:
    readme = readme_file.read()


setup(
    name="HDrezka",
    version=HDrezka.__version__,
    packages=find_packages(),
    long_description=readme,

)