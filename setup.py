import os
import re

from setuptools import setup, find_packages

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "HDrezka", "__version__.py"), "r", encoding="utf-8") as f:
    text = re.sub(r"[\"\']\s*?\\\n\s*?[\"\']", "", f.read())
    for line in text.strip().split("\n"):
        name, value = re.search(r"(.*?)\s*?=\s*?[\"\'](.*?)[\"\']$", line).groups()
        about[name.strip()] = value.strip()

with open("requirements.txt", "r", encoding="utf-8") as requirement_file:
    requires = list(map(str.strip, requirement_file.readlines()))

with open("requirements-dev.txt", "r", encoding="utf-8") as requirement_file:
    dev_requires = list(map(str.strip, requirement_file.readlines()))

with open('README.md', encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__contact__"],
    url=about["__url__"],
    packages=find_packages(include=["HDrezka", "HDrezka.*"]),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requires,
    license=about["__license__"],
    keywords="hdrezka,hdrezka-api,rezka,rezka-api,movie,film,api",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    tests_require=dev_requires,
    project_urls={
        "Documentation": "",
        "Source": "https://github.com/kristal374/hdrezka-api",
    },
)
