# Pecha API

This is the backend API for the Pecha application.


### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/pecha_api.git
    ```
2. Navigate to the project directory:
    ```sh
    cd pecha_api
    ```
3. Install the dependencies:
    ```sh
    poetry install
    ```

### Database Setup

```sh
  cd local_setup
  docker-compose up -d
```
```sh
 poetry run alembic upgrade
```

### Running the Application

1. Start the FastAPI development server:
    ```sh
    poetry run uvicorn pecha_api.app:api --reload
    ```

The application will be available at `http://127.0.0.1:8000/`.

### Running Tests

To run tests, execute the following command:
```sh
poetry run pytest
```