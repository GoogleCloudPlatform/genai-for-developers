from setuptools import setup

setup(
    name='devai',
    version='0.1.0',
    py_modules=['devai'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'devai = devai:devai',
        ],
    },
)