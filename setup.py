from setuptools import setup, find_namespace_packages

setup(
    name="hockey_stats",
    version="0.1.0",
    packages=find_namespace_packages(include=["hockey_stats", "hockey_stats.*"]),
    install_requires=[
        "streamlit>=1.33.0",
        "gspread>=6.0.2",
        "pandas>=2.0.3",
        "numpy>=1.26.4",
        "google-auth>=2.27.0",
    ],
    python_requires=">=3.9",
)
