#!/usr/bin/env python

from setuptools import setup

setup(
    name="adjure",
    license="MIT",
    description="Two-factor authentication microservice",
    author="Ben Picolo",
    author_email="be.picolo@gmail.com",
    url="https://github.com/bpicolo/adjure",
    packages=["adjure"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=[
        'cryptography',
        'flask',
        'jsonschema',
        'logstash-formatter',
        'pillow',
        'qrcode',
        'uwsgi',
        'yaml',
    ],
)
