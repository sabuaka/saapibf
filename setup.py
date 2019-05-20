'''setup.py'''
from setuptools import setup
setup(
    name='saapibf',
    packages=['saapibf'],
    version='0.0.1',
    description='bitFlyer API Library for Python',
    author='sabuaka',
    author_email='sabuaka-fx@hotmail.com',
    url="https://github.com/sabuaka/saapibf",
    install_requires=[
        'requests==2.21.0',
        'urllib3==1.25.2',
        'websocket-client==0.48.0'
    ]
)
