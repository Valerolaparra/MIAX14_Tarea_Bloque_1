from setuptools import setup, find_packages

setup(
    name="valerolaparra",
    version="0.1.0",
    description="Herramienta completa para análisis bursátil y simulaciones",
    author="Tu Nombre",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "yfinance>=0.2.28",
        "requests>=2.31.0",
        "scipy>=1.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "market-analysis=src.cli:main",
        ],
    },
)