import os
import functools
from setuptools import setup, find_packages

_IN_PACKAGE_DIR = functools.partial(os.path.join, "metrics")

with open(_IN_PACKAGE_DIR("__version__.py")) as version_file:
    exec(version_file.read())

setup(name="metrics",
      classifiers = [
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2.7",
          ],
      description="Performance metrics, based on Coda Hale's Yammer metrics",
      license="Proprietary",
      author="Infinidat Ltd.",
      author_email="",
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      data_files = [],
      install_requires=[
          ],
      scripts=[],
      )
