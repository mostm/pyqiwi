#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
from pyqiwi.__version__ import __version__

try:
    with open('README.txt', encoding='utf-8') as readme_file:
        readme = readme_file.read()
except FileNotFoundError:
    # I should investigate why this is a case.
    readme = "Python QIWI API Wrapper"

try:
    with open('HISTORY.rst', encoding='utf-8') as history_file:
        history = history_file.read()
except FileNotFoundError:
    # thats fine, we are building on Travis
    history = ''

requirements = ['six', 'requests>=2.15,<3', 'parse>=1.8,<2', 'python-dateutil>=2.7,<3']

setup_requirements = ['pytest-runner', 'six', 'requests>=2.15,<3', 'parse>=1.8,<2', 'python-dateutil>=2.7,<3']

test_requirements = ['pytest', 'six', 'requests>=2.15,<3', 'parse>=1.8,<2', 'python-dateutil>=2.7,<3']

setup(
    author="Levent Duivel",
    author_email='mostm@endcape.ru',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Python Qiwi API Wrapper",
    install_requires=requirements,
    license="MIT",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/plain",
    include_package_data=True,
    keywords='pyqiwi',
    name='qiwipy',
    packages=find_packages(include=['pyqiwi']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mostm/pyqiwi',
    version=__version__,
    zip_safe=False,
)
