# MovieApp

MovieApp is a console application written in Python3 for managing a database of movies, directors, and actors.

## Prerequisites

Before running the application, ensure you have the following:

- Python3 installed
- Virtual environment set up
- PostgreSQL database server running
- Docker installed (optional, for running containers)

## Setup

1. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:

    - On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - On Unix:

        ```bash
        source venv/bin/activate
        ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run PostgreSQL and Adminer containers (optional):

    ```bash
    docker-compose up --build -d
    ```

## Running the Application

To run the application, execute the following command:

```bash
python app.py


Usage
Upon successful startup, the application supports the following commands:

l: List movies
l -v: Detailed view of a movie
l -t "regex": Filter movies by title regex
l -d "regex": Filter movies by director regex
l -a "regex": List movies with actors matching the regex
l -la or l -ld: List movies with ascending or descending order by length
a -p: Add a new person to the database
a -m: Add a new movie to the database
d -p "name": Delete a person from the database
