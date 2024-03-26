from setuptools import setup, find_packages

setup(
    name="devaicli",
    version="0.0.2a3",
    description="Devai cli ",
    packages=find_packages(),  
    python_requires='>=3.6',               
    py_modules=["devai"], 
    install_requires=[
        'devaicore',
        'click==8.1.7',
        'google-cloud-aiplatform'
    ],
    entry_points={
        'console_scripts': [
            'devai = devai.cli:devai',
        ],
    },
)
