from setuptools import setup, find_packages

setup(
    name="monkeylogs",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "gunicorn",
        "numpy",
        "matplotlib",
        "click"
    ],
    entry_points={
        "console_scripts": [
            "monkeylogs=monkeylogs.cli:main"
        ],
    },
)