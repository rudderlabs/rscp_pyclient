import setuptools

long_description = """
# RudderStack Control Plain Client 
Use this package to interact with RudderStack Control Plain REST API.

## Pre Requisites 
Python 3.8
Bash
Python Modules: Flask, Requests, Flask_Cors

## Using
pip install https://github.com/rudderlabs/rscp_pyclient/
"""

setuptools.setup(
    name='rscp_pyclient',
    version='0.0.1',
    author='Nishant Sharma',
    author_email='nishant@goalsmacker.in',
    description='This package(RudderStack Control Plain Python Client) includes python functions to execute CRUD operations on REST API exported by RudderStack.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/rudderlabs/segment-migrator',
    project_urls = {
        "Bug Tracker": "https://github.com/rudderlabs/segment-migrator/issues"
    },
    license='MIT',
    packages=['rscp_pyclient'],
    install_requires=['flask', 'flask_cors', 'requests'],
)
