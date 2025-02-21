from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="rpa-project",
    version="1.0.0",
    description="Sistema de automação para análise de dados e geração de relatórios",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Sua Equipe",
    author_email="suporte@empresa.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.2.0",
        "openpyxl>=3.0.0",
        "PyYAML>=5.4.0",
        "reportlab>=4.0.0",
        "pydantic>=2.0",
        "pydantic-settings>=2.0",
        "matplotlib>=3.7.0"
    ],
    entry_points={
        "console_scripts": [
            "rpa-project=main:main",
        ],
    },
    package_data={
        "rpa_project": [
            "config.yaml",
            "assets/*"
        ],
    },
    project_urls={
        "Documentação": "https://github.com/seu-repositorio/docs",
        "Código Fonte": "https://github.com/seu-repositorio/rpa-project",
    },
)
