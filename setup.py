# -*- coding: utf-8 -*-

from setuptools import setup
import re
import sys

version = ''
with open('frost/__init__.py', 'r') as f:
    version = re.search(r'__version__\s*=\s*\'([\d.]+)\'', f.read()).group(1)

with open('README.rst') as f:
    readme = f.read()

with open('HISTORY.rst') as f:
    history = f.read()

requirements = [
    'Flask',
    'flask-hookserver',
    'redis',
    'requests',
]
if sys.version_info < (3, 3):
    requirements.append('ipaddress')

setup(
    name='frost',
    version=version,
    author='Nick Frost',
    author_email='nickfrostatx@gmail.com',
    url='https://frost-ci.xyz',
    description='Totally not a Travis clone.',
    long_description=readme + '\n\n' + history,
    packages=[
        'frost',
    ],
    install_requires=requirements,
    extras_require={
        'testing': [
            'blinker',
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'pytest-pep257',
        ],
    },
    license='MIT',
    keywords='frost',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
