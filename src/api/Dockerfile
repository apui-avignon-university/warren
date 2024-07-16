# -- Base image --
FROM fundocker/warren:api-core-0.5.0 AS base

# -- Builder --
FROM base AS builder

WORKDIR /build

# Should be a priviledged user
USER root:root

COPY . /build/

RUN pip install ./plugins/tdbp

# -- Core --
FROM base AS core

COPY --from=builder /usr/local /usr/local

WORKDIR /app

USER root:root

# Install curl for docker healthchecks and jq for API doc provisioning
RUN  apt-get update && \
     apt-get install -y \
          curl \
          jq && \
     rm -rf /var/lib/apt/lists/*

# -- Development --
FROM core AS development

# Should be a priviledged user
USER root:root

# Copy all sources
COPY ./plugins/tdbp /app/plugins/tdbp

# Uninstall warren and re-install it in editable mode along with development
# dependencies
RUN pip uninstall -y warren-tdbp
RUN pip install -e plugins/tdbp[dev]

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}

# -- Production --
FROM core AS production

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}

CMD ["uvicorn", \
     "warren.api:app", \
     "--proxy-headers", \
     "--log-config", \
     "logging-config.prod.yaml", \
     "--host", \
     "0.0.0.0", \
     "--port", \
     "8000"]
