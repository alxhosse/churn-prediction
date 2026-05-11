FROM python:3.13-slim

WORKDIR /opt/program

RUN pip install --no-cache-dir uv

COPY ml/containers/requirements-inference.txt .

RUN uv pip install --system -r requirements-inference.txt

COPY ml/src/churn_ml /opt/program/churn_ml

ENTRYPOINT ["python", "-m", "churn_ml.inference"]