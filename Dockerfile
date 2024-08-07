FROM mcr.microsoft.com/vscode/devcontainers/python

COPY requirements.txt .
RUN pip install -r requirements.txt