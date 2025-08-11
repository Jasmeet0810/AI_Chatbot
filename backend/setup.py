from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lazulite-ai-ppt-generator",
    version="1.0.0",
    author="Lazulite Team",
    author_email="info@lazulite.ae",
    description="AI-powered PowerPoint generation from Lazulite product data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lazulite/ai-ppt-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.24.0",
            "factory-boy>=3.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lazulite-api=app.main:main",
            "lazulite-worker=run_worker:main",
            "lazulite-beat=run_beat:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["templates/*.pptx"],
    },
)