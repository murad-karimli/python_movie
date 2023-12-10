CREATE TABLE People ( 
    id SERIAL PRIMARY KEY, 
    name VARCHAR(255) NOT NULL, 
    birth_year INTEGER 
); 
 
CREATE TABLE Movies ( 
    id SERIAL PRIMARY KEY, 
    title VARCHAR(255) NOT NULL, 
    director_id INTEGER REFERENCES People(id), 
    release_year INTEGER, 
    length INTERVAL, 
    CONSTRAINT unique_movie_title_director UNIQUE (title, director_id) 
); 
 
CREATE TABLE MovieCast ( 
    movie_id INTEGER REFERENCES Movies(id), 
    person_id INTEGER REFERENCES People(id), 
    PRIMARY KEY (movie_id, person_id) 
); 
