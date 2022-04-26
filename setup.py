import os.path
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

README_PATH = os.path.join(HERE, 'README.md')
try:
    README = open(README_PATH).read()
except IOError:
    README = ''

setup(
  name='splicer',

  version="0.3.0",
  description='the world is a database now you can query it with SQL',
  long_description=README,
  author='Scott Robertson',
  author_email='scott@triv.io',
  url='http://github.com/trivio/splicer',
  classifiers=[
      "Programming Language :: Python :: 3.10",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Intended Audience :: Developers",
      "Topic :: Software Development",
  ],
  python_requires='>=3.8',
  packages = find_packages(),
  package_data={"splicer": ["py.typed"]},
  install_requires=[
    'codd',
    'zipper',
  ]
)
