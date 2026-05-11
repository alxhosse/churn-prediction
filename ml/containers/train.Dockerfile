FROM python:3.13-slim

WORKDIR /opt/program

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY ml/containers/requirements-train.txt .

RUN uv pip install --system -r requirements-train.txt

COPY ml/src/churn_ml /opt/program/churn_ml

ENTRYPOINT ["python", "-m", "churn_ml.train"]