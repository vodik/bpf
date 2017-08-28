#!/usr/bin/env python
"""The setup script."""

from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Distutils import build_ext

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pyparsing'
]

ext_modules = [
    Extension("idea.struct", ["idea/struct.pyx"], language="c++",
              extra_compile_args=["-std=c++11"])
]

setup(
    name='bpf',
    version='0.1.0',
    description="BPF compiler and utilities",
    long_description=readme + '\n\n' + history,
    author="Simon Gomizelj",
    author_email='simon@vodik.xyz',
    url='https://github.com/vodik/aioraw',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords=['bpf', 'linux', 'sockets', 'networking'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules
)
