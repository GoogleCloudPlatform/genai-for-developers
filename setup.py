from setuptools import setup

setup(
    name='dai',
    version='0.1.0',
    py_modules=['dai'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'dai = gcloudai.hello:cli',
        ],
    },
)