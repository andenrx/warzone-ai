from setuptools import setup, find_packages

setup(
    name='warzone-ai',
    version='0.1',
    description='Warzone AI',
    url='https://github.com/andenrx/warzone-ai',
    author='Andrew Bauer',
    author_email='arbauer@amazon.com',
    packages=['wzai'],
    install_requires=[
       "numpy",
       "requests",
       "networkx",
       "wonderwords",
    ],
    extras_require={
        "nn": [
            "torch",
            "torch-scatter",
            "torch-sparse",
            "torch-geometric",
        ]
    },
)
