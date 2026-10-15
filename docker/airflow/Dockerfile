FROM apache/airflow:2.10.5-python3.11

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-${TARGETARCH}

USER airflow
# Same packages as your local .venv, in their own venv so they don't clash with Airflow's.
COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /home/airflow/venv \
    && /home/airflow/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt
