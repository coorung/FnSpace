# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 09:34:51 2024

@author: coorung77
"""

from setuptools import setup, find_packages

setup(
    name='fnspace',
    version='0.3.2',
    description='A utility to fetch financial data',
    author='Ungjin Jang',
    author_email='coorung77@gmail.com',
    url='https://github.com/coorung/FnSpace',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)