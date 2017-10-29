from setuptools import setup
from pyqiwi import __version__

name = 'qiwipy'
lib_filename = 'pyqiwi'
version = __version__

desc = 'Python Qiwi API Wrapper'
long_desc = open('README.md', 'r', encoding='utf-8').read()
github = 'https://github.com/mostm/pyqiwi'
author = 'mostm'
author_email = 'mostm@endcape.ru'
license_type = 'MIT'
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
keywords = 'qiwi python api wrapper lib'
install_requires = ['requests>=2.18.4,<3']


setup(
    name=name,
    version=version,
    description=desc,
    long_description=long_desc,
    url=github,
    license=license_type,
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    keywords=keywords,
    install_requires=install_requires,
    packages=[lib_filename]
)
