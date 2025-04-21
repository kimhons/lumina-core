from setuptools import setup, find_packages

setup(
    name="lumina-core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "websockets>=11.0.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
    ],
    author="Lumina AI Team",
    author_email="team@luminaai.com",
    description="Central orchestration and core services for Lumina AI",
    keywords="ai, agent, orchestration",
    python_requires=">=3.10",
)
