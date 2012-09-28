#!/usr/bin/env python

from distutils.core import setup
import ot

setup(
  name='ot',
  version=ot.__version__,
  description='Operational Transformations for collaborative editing',
  author='Tim Baumann',
  author_email='tim@timbaumann.info',
  packages=['ot'],
)
