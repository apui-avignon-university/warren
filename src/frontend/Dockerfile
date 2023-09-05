# -- Base image --
FROM warren-frontend:development as base

# -- Development --
FROM base as development

COPY . /app/packages/tdbp

# Install plugin
USER root
RUN yarn install

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}
