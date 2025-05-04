from setuptools import setup, find_packages

setup(
    name='financial_pipeline',
    version='0.1.0',
    description='A modular pipeline for importing, cleaning, storing, and displaying financial data.',
    author='Vincent Réau',
    author_email='vincent.reau1@gmail.com',
    packages=find_packages(exclude=["tests", "scripts"]),
    python_requires='>=3.7',
    install_requires=[
        'requests',   # importer part
        'yfinance',
        'numpy',      # cleaner/importer part
        'pandas',     
        'streamlit',  # interface part
        'seaborn',
        'altair',
        'sklearn',    # ml part
    ],
    entry_points={
        'console_scripts': [
            'run-financial-pipeline=scripts.run_pipeline:run',
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',  # if applicable
        'Topic :: Database',
        'Topic :: Utilities',
    ],
)
