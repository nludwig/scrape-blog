#!/usr/bin/env python3

import setuptools

setuptools.setup(
    'name': 'scrape-blog',
    'version': 0.0.1,
    'description': 'Tool to scrape SSC and maybe other simple blogs.',
    'author': 'Nick Ludwig',
    'author_email': 'nick.b.ludwig@gmail.com',
    'install_requires': [
        'beautifulsoup4',
        'python-docx',
        'requests',
    ],
)
