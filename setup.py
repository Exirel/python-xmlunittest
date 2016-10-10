# -*- coding: utf-8 -*-
"""Python-xmlunittest.

Python library for unit-testing of XML document using lxml.

- Distribution: https://pypi.python.org/pypi/xmlunittest
- Documentation: http://python-xmlunittest.readthedocs.org/en/latest/
- Source: https://github.com/Exirel/python-xmlunittest

"""
import codecs
import os

from setuptools import setup


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts),
                       encoding='utf-8').read()


classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Testing',
    'Topic :: Text Processing :: Markup :: XML'
]

setup(name='xmlunittest',
      version='0.4.0',
      description='Library using lxml and unittest for unit testing XML.',
      long_description=read('README.rst'),
      author='Florian Strzelecki',
      author_email='florian.strzelecki@gmail.com',
      license='MIT',
      url='http://python-xmlunittest.readthedocs.org/en/latest/',
      py_modules=['xmlunittest'],
      test_suite="test",
      install_requires=['lxml>=2.3,<4.0.0'],
      classifiers=classifiers)
