#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'PIL',
    'sqlite3',
    'argparse'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='slippy_sqlite_generator',
    version='0.1.0',
    description="Creates a sqlite database using the Slippy naming convention from input image with world file.",
    long_description=readme + '\n\n' + history,
    author="Blair Shaman",
    author_email='bjs339@yahoo.com',
    url='',
    packages=[
        'slippy_sqlite_generator',
    ],
    package_dir={'slippy_sqlite_generator':
                 'slippy_sqlite_generator'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='slippy_sqlite_generator',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
