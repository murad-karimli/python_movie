@echo off

REM Variables
SET DB_CONTAINER_NAME=postgres
SET DB_USER=root
SET DB_PASSWORD=admin
SET DB_NAME=movie

REM Save SQL commands to a file
echo CREATE TABLE People ( > create_tables.sql
echo     id SERIAL PRIMARY KEY, >> create_tables.sql
echo     name VARCHAR(255) NOT NULL, >> create_tables.sql
echo     birth_year INTEGER >> create_tables.sql
echo ); >> create_tables.sql
echo. >> create_tables.sql
echo CREATE TABLE Movies ( >> create_tables.sql
echo     id SERIAL PRIMARY KEY, >> create_tables.sql
echo     title VARCHAR(255) NOT NULL, >> create_tables.sql
echo     director_id INTEGER REFERENCES People(id), >> create_tables.sql
echo     release_year INTEGER, >> create_tables.sql
echo     length INTERVAL, >> create_tables.sql
echo     CONSTRAINT unique_movie_title_director UNIQUE (title, director_id) >> create_tables.sql
echo ); >> create_tables.sql
echo. >> create_tables.sql
echo CREATE TABLE MovieCast ( >> create_tables.sql
echo     movie_id INTEGER REFERENCES Movies(id), >> create_tables.sql
echo     person_id INTEGER REFERENCES People(id), >> create_tables.sql
echo     PRIMARY KEY (movie_id, person_id) >> create_tables.sql
echo ); >> create_tables.sql

REM Run SQL commands in the PostgreSQL container
docker exec -i %DB_CONTAINER_NAME% psql -U %DB_USER% -d %DB_NAME% -f /var/lib/postgresql/data/create_tables.sql
