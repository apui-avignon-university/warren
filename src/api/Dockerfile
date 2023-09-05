# -- Base image --
# FIXME: use an official release instead
FROM warren-api:development as base

# -- Development --
FROM base as development

# Copy all sources, not only runtime-required files
COPY . /app/plugins/tdbp

# Install plugin in editable mode along with development dependencies
USER root
RUN pip install -e ./plugins/tdbp

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}
