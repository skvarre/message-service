# message-service
A simple message service REST API built with Python [Flask](https://flask.palletsprojects.com/en/3.0.x/), using [SQLAlchemy](https://www.sqlalchemy.org/) for Object Relational Mapping and [Swagger UI](https://swagger.io/tools/swagger-ui/) for API documentation. 

## Build & Run 

### Option 1 - pip

The project can be built (preferably using a virtual environment) by installing the required dependencies in `requirements.txt`: 

```bash
pip install -r requirements.txt
```

The API service can be started by running `api.py` in the `src/` directory. 

```bash
python api.py
```

This will serve the API on `http://localhost:5000/`, instantiating a local sqlite database in `src/instace/messages.db`.

### Option 2 - Docker Compose

Alternatively, the application can be built and run from within a container using `docker-compose`:

```bash
docker-compose up --build
```

This will build the Docker image and start the container. The API will be available at `http://localhost:5000`. 

## Documentation

Once the service is running, both API specification can be found and requests can be made from `http://localhost:5000/apidocs`.

For consistency, information about the endpoints are also shown below.
