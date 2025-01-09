from setuptools import setup

setup(
    name='trading_bot',
    version='0.1',
    install_requires=[
        'streamlit',
        'gh-pages'
    ],
    entry_points={
        'console_scripts': [
            'streamlit=streamlit.cli:main',
        ],
    },
)
