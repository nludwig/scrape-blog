#!/usr/bin/env python3

import setuptools

readme = 'README.md'
with open(readme) as f:
    long_description = f.read()

setuptools.setup(
    name='scrape-blog',
    version='0.0.1',
    author='Nick Ludwig',
    author_email='nick.b.ludwig@gmail.com',
    description='Tool to scrape SSC and maybe other simple blogs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nludwig/scrape-blog',
    packages=setuptools.find_packages(),
    install_requires=[
        'beautifulsoup4',
        'python-docx',
        'requests',
    ],
    entry_points={
        'console_scripts': ['scrape-ssc = scrape_blog.scrape_ssc:main'],
    },
)
