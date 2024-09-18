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

Once the service is running, the API specification can be found at `http://localhost:5000/apidocs`. Requests can also be made directly from the Swagger UI.

For consistency, information about the endpoints are also shown below.

___
### POST /messages

- **Description:** Submit a message to a recipient user. 
- **Method**: `POST`
- **Endpoint**: `/messages`
- **cURL Example**:
```bash
curl -X POST 'http://127.0.0.1:5000/messages' \
-H  'accept: application/json' \
-H  'Content-Type: application/json' \
-d '{
    "sender": "LeifGW",
    "recipient": "Kungen",
    "content": "Tjenare kungen!"
}'
```
- **Response Sample**:
```json
{
  "message": "Message sent successfully"
}
```
___
### GET /messages/new

- **Description:** Retrieve all new messages for a recipient user.
- **Method**: `GET`
- **Endpoint**: `/messages/new`
- **cURL Example:**
```bash
curl -X GET 'http://127.0.0.1:5000/messages/new?recipient=Kungen' \
-H 'accept: application/json'
```
- **Response Sample:**
```json
{
  "messages": 
  [
    {
      "content": "Tjenare kungen!",
      "id": 1,
      "recipient": "Kungen",
      "sender": "LeifGW",
      "timestamp": "Wed, 18 Sep 2024 11:38:30 GMT"
    }
  ]
}
```
___
### DELETE /messages/{id}

- **Description:** Delete a message by its ID.
- **Method**: `DELETE`
- **Endpoint**: `/messages`
- **cURL Example:**
```bash
curl -X DELETE 'http://127.0.0.1:5000/messages/1' \
-H 'accept: application/json'
```
- **Response Sample:**
```json
{
  "message": "Message deleted successfully"
}
```
___
### DELETE /messages

- **Description:** Delete multiple messages for a recipient user.
- **Method**: `DELETE`
- **Endpoint**: `/messages`
- **cURL Example:**
```bash
curl -X DELETE 'http://127.0.0.1:5000/messages' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
    "ids": [2, 3]
}'
```
- **Response Sample:**
```json
{
  "message": "Successfully deleted all messages"
}
```
___
### GET /messages

- **Description:** Fetches messages to the recipient user, based on start and stop indexes in order of time received, regardless of whether the messages has been read or not.
- **Method**: `GET`
- **Endpoint**: `/messages`
- **cURL Example:**
```bash
curl -X GET 'http://127.0.0.1:5000/messages?recipient=Kungen&start_index=0&stop_index=2'\
-H 'accept: application/json'
```
- **Response Sample:**
```json
{
  "messages": [
    {
      "content": "Ska vi ta en fisketur tro?",
      "id": 6,
      "recipient": "Kungen",
      "sender": "LeifGW",
      "timestamp": "Wed, 18 Sep 2024 12:08:44 GMT"
    },
    {
      "content": "Tjenare kungen!",
      "id": 5,
      "recipient": "Kungen",
      "sender": "LeifGW",
      "timestamp": "Wed, 18 Sep 2024 11:48:25 GMT"
    }
  ],
  "start_index": 0,
  "stop_index": 2,
  "total_messages": 2
}
``` 