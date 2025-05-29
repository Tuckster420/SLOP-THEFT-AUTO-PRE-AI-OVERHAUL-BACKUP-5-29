from setuptools import setup, find_packages

setup(
    name="stinkworld",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        'console_scripts': [
            'stinkworld=stinkworld.core.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'stinkworld': ['sprites/*', 'data/*'],
    },
    python_requires='>=3.8',
    author="Original Author",
    description="StinkWorld - A Python-based open-world game",
    keywords="game, pygame, open-world",
) 