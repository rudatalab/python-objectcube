#!/usr/bin/env python
# # coding: utf-8
from setuptools import find_packages, setup

description = 'Implementation of the ObjectCube model, defined by ' \
              'Grimur Tomasson <grimurt@ru.is> and Bjorn Thor ' \
              'Jonsson <bjorn@ru.is>'

package_name = 'python-objectcube'
authors = 'hlysig, siggirh'
authors_email = 'hlysig@gmail.com'
requirements = ''.join(open('requirements.txt').readlines()).split('\n')

setup(
    name='python-objectcube',
    description=description,
    version='0.0.1',
    long_description=description,
    author=authors,
    author_email=authors_email,
    url='https://github.com/rudatalab/{0}'.format(package_name),
    install_requires=requirements,
    packages=find_packages()
)
