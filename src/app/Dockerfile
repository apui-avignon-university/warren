# -- Base image --
FROM  fundocker/warren:app-0.2.0

# Privileged user
USER root:root
# Clean up frontend static files

# Nota bene: it requires that the frontend application to be already built
RUN rm -fr /app/staticfiles/warren/* && mkdir -p /app/staticfiles/warren/assets/
COPY ./staticfiles/warren/assets/index.js \
        ./staticfiles/warren/assets/index-*.js \
        ./staticfiles/warren/assets/index.css \
        /app/staticfiles/warren/assets/

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}
