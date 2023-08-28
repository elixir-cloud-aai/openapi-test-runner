from pathlib import Path
from setuptools import (setup, find_packages)

with open('README.md', 'r') as fh:
    long_description = fh.read()

root_dir = Path(__file__).parent.resolve()
req = root_dir / 'requirements.txt'
with open(req, 'r') as _file:
    install_requires: list = _file.read().splitlines()

setup(
    name='openapi-compliance-suite',
    version='0.1.0',
    description='OpenAPI Compliance Suite to perform conformance testing to API specs and functionality',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/elixir-cloud-aai/tes-compliance-suite',
    author='Lakshya Garg',
    author_email='garg.lakshya@gmail.com',
    maintainer='ELIXIR Cloud & AAI',
    maintainer_email='cloud-service@elixir-europe.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Typing :: Typed',
    ],
    entry_points={
        'console_scripts': [
            'compliance-suite = compliance_suite.cli:main',
        ],
    },
    keywords=(
        'elixir rest api app server openapi '
        'python compliance testing pydantic yaml '
    ),
    project_urls={
        'Repository': 'https://github.com/elixir-cloud-aai/tes-compliance-suite',
        'ELIXIR Cloud & AAI': 'https://elixir-europe.github.io/cloud/',
        'Tracker': 'https://github.com/elixir-cloud-aai/tes-compliance-suite/issues',
    },
    license='Apache License 2.0',
    packages=find_packages(exclude=[
        'unittests',
        'unittests.*'
    ]),
    package_data={'': ['test_config/*', 'web/*/*']},
    install_requires=install_requires,
)
