from setuptools import setup, find_packages

setup(
    name="devai_cli",
    version="0.0.0",
    description="Devai cli ",
    packages=find_packages(),  # Finds 'devai_cli'
    install_requires=['devai_core']  # List any external dependencies here
)
