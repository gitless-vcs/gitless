#!/usr/bin/env python

from setuptools import setup


setup(
    name='gitless',
    version='0.4',
    description='A version control system built on top of Git',
    long_description=open('README.md').read(),
    author='Santiago Perez De Rosso',
    author_email='sperezde@csail.mit.edu',
    url='http://github.com/spderosso/gitless',
    packages=['gitless'],
    install_requires=['gitpylib>=0.4'],
    license='GPLv2',
    classifiers=(
      'Development Status :: 2 - Pre-Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Software Development :: Version Control'
      ),
    entry_points={
      'console_scripts': [
        'gl = gitless.cli.gl:main'
        ]
      },
    test_suite='gitless.tests'
    )
