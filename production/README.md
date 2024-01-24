# Deploy Warren-TdBP with Docker Swarm

## Dependencies

- [Docker Engine](https://docs.docker.com/engine/install/) with Swarm mode

## Tutorial

This quick tutorial aims at deploying Warren-TdBP on a local Docker Engine cluster in
swarm mode. In this tutorial, you will learn to:

- run and configure a small cluster of Docker Engines in swarm mode on your machine,
- deploy Warren TdBP from the production Compose file.

Initialize a local cluster with the command:
```bash
docker swarm init
```

We can view the current state of the swarm with:
```bash
docker info
```

We can view information about nodes with:
```bash
docker node ls
```

> In this tutorial, we will deploy Warren-TdBP on a single node cluster. If you want to
> add more nodes to the cluster, refer to this
> [documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/add-nodes/).

### Creating the volumes

Warren-TdBP `app` and `api` services need a PostgreSQL database for persistency. We need
to create a Docker volume for the database, but also for the static and media files
(required by the `app` service).

In this tutorial, we'll create three volumes:
```bash
docker volume create postgresql_data
docker volume create media
docker volume create static
```

> For more options on the volume creation (size, file system, device, etc.), you can
> refer to this
> [documentation](https://docs.docker.com/engine/reference/commandline/volume_create/).

### Creating the logging config

To adjust services logging configuration, you can create a new `config` object from the
project's sources:

```bash
docker config create logging_config.yaml src/api/logging-config.prod.yaml
```

In this example, we are creating a new config called `logging_config.yaml` from the
content of the `src/api/logging-config.prod.yaml` file. This config will be mounted
under the `/app/core/` directory of the `api` service during the deployment.

### Deploying Warren-TdBP

Docker Engine in swarm mode can deploy services defined in a Compose file. We are going
to deploy three services: `postgresql`, `api` and `app`. 

You can adjust the `docker-compose.prod.yml` file to fit your needs, along with the
three environment files: `postgresql.env`, `api.env` and `app.env`. Pay attention to
Warren's docker images tags.

When you're ready, let's deploy our services: 
```bash
docker stack deploy --compose-file production/docker-compose.prod.yml
```

We can check if our services are up and running with:
```bash
docker service ls
```

And we can see all the running containers with:
```bash
docker ps
```

If a service is not healthy, we can investigate further with:
```bash
docker inspect --format "{{json .State.Health }}" CONTAINER_ID | jq
```
_Nota bene_: this command requires that [jq](https://jqlang.github.io/jq/) is installed
on your operating system.