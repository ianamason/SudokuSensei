"""pip package definition."""
from os import path

import subprocess

# from distutils.core import setup
from setuptools import setup, find_packages

# use the in house version number so we stay in synch with ourselves.
from sudokusensei.Version import sudoku_sensei_version

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

subprocess.call(['make', '-C', 'sudoku/lib', 'lib'])

setup(
    name='sudoku',
    version=sudoku_sensei_version,
    description='The SMT Sudoku Sensei',
    long_description=long_description,
    url='https://github.com/ianamason/SudokuSensei',
    author='Ian A. Mason',
    author_email='iam@csl.sri.com',


    packages=find_packages(exclude=['tests']),

    package_data={
        'sudokusensei':  ['data/*.sudoku', 'lib/libsugen.*'],
    },



    entry_points={
        'console_scripts': [
            'sudokusensei = sudokusensei.Main:main',
            'senseitest = sudokusensei.TestMain:main',
        ],
    },


    license='CC4',

    install_requires=[
        'yices >= 1.1.3'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
