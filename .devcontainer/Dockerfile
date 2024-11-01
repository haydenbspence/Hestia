FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    unixodbc \
    unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages needed for development
RUN pip install --no-cache-dir \
    ruff \
    black \
    pytest \
    pytest-cov \
    ipython \
    jupyterlab \
    ibis-framework[duckdb,postgres,mysql,sqlite] \
    motherduck \
    duckdb \
    sqlalchemy \
    fastapi \
    uvicorn \
    python-dotenv \
    pandas \
    numpy \
    scipy \
    matplotlib \
    seaborn \
    pyarrow \
    polars

# Install Node.js (required for some Quarto features)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Add vscode user to the correct groups
RUN usermod -aG staff,users vscode

# Create directory for MotherDuck configuration
RUN mkdir -p /home/vscode/.motherduck && chown vscode:vscode /home/vscode/.motherduck
