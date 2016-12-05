#!/usr/bin/env python

import re

from setuptools import setup

package = [vivobot]
requires = []
test_requirements = ['pytest>=2.8.0']

with open('vivobot/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='VIVOBot',
    version=version,
    description='VIVO task automation',
    long_description=readme,
    author='Nate Prewitt',
    author_email='nate.prewitt@gmail.com',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'vivobot': 'vivobot'},
    include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
    tests_require=test_requirements
)

