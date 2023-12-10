import psycopg2
from psycopg2 import sql
import os
import subprocess
from datetime import datetime
import re
import json
    
class MovieDatabase:
    def __init__(self, connection_options):
        self.connection_options = connection_options
        self.check_and_create_tables()
        self.people = [] 

    def execute_query(self, query, params: tuple=None):
        with psycopg2.connect(**self.connection_options) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                conn.commit()

    def check_and_create_tables(self):
        # Check if tables exist
        query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'people' OR table_name = 'movies' OR table_name = 'moviecast');"
        result = self.execute_query(query)
        tables_exist = result[0][0]

        if not tables_exist:
            # Tables do not exist, run create-tables.sh script
            self.run_create_tables_script()

    def run_create_tables_script(self):
        # Use os.path to join paths
        script_path = os.path.join(os.path.dirname(__file__), 'create-tables.bat')
        subprocess.run([script_path])

    def list_movies(self, verbose=False, title_regex=None, director_regex=None, actor_regex=None, ascending=True):
        query = "SELECT * FROM movies"
        # Apply filters based on regex if provided
        if title_regex:
            query += f" WHERE title ~ '{title_regex}'"
        if director_regex:
            query += f" AND director ~ '{director_regex}'"
        if actor_regex:
            query += f" AND EXISTS (SELECT 1 FROM moviecast WHERE movies.id = moviecast.movie_id AND EXISTS (SELECT 1 FROM people WHERE people.id = moviecast.person_id AND name ~ '{actor_regex}'))"
        # Apply ordering
        query += f" ORDER BY length {'ASC' if ascending else 'DESC'}, title ASC"
        # Execute the query
        result = self.execute_query(query)
        # Display the movies
        for movie in result:
            self.print_movie(movie, verbose)

    def add_person(self, name, birth_year):
        query = "INSERT INTO People (name, birth_year) VALUES (%s, %s) RETURNING *;"
        params = (name, birth_year)

        try:
            result = self.execute_query(query, params)
            new_person = result[0] if result else None
            if new_person:
                self.people.append({'id': new_person[0], 'name': new_person[1], 'birth_year': new_person[2]})
                print(f"Person '{name}' added to the database.")
            else:
                print("Error adding person.")
        except Exception as e:
            print(f"Error adding person: {e}")

    def add_movie(self, title, length, director, release_year, actors):
        # Check if the director exists
        director_id = self.get_person_id(director)
        if not director_id:
            print(f'Error: Director "{director}" not found in the database. Please add the director first.')
            return

        # Insert the movie into the Movies table
        query = "INSERT INTO movies (title, director_id, release_year, length) VALUES (%s, %s, %s, %s) RETURNING id"
        movie_id = self.execute_query(query, (title, director_id, release_year, length))[0][0]

        # Insert the movie cast into the MovieCast table
        for actor in actors:
            actor_name = actor['name']
            actor_id = self.get_person_id(actor_name)
            if actor_id:
                # Insert the cast only if the actor exists
                query = "INSERT INTO moviecast (movie_id, person_id) VALUES (%s, %s)"
                self.execute_query(query, (movie_id, actor_id))
            else:
                print(f'Error: Actor "{actor_name}" not found in the database. Please add the actor first.')
                return  # Stop the process if an actor is not found
            
    def delete_person(self, name):
        # Delete a person from the People table
        query = "DELETE FROM people WHERE name = %s RETURNING id"
        result = self.execute_query(query, (name,))
        if result:
            person_id = result[0][0]
            # Delete the person from the MovieCast table
            query = "DELETE FROM moviecast WHERE person_id = %s"
            self.execute_query(query, (person_id,))
        else:
            print(f'Error: Person "{name}" not found in the database.')

    def save_data(self):
        # Save data - not needed in this implementation
        pass

    def get_person_id(self, name):
        # Get the ID of a person from the People table
        query = "SELECT id FROM people WHERE name = %s"
        result = self.execute_query(query, (name,))
        return result[0][0] if result else None

    def print_movie(self, movie, verbose=False):
        # Display movie information
        print(f"{movie[1]} by {self.get_person_name(movie[2])} in {movie[3]}, {movie[4]}")
        if verbose:
            print('Starring:')
            cast_query = "SELECT people.name, people.birth_year FROM moviecast JOIN people ON moviecast.person_id = people.id WHERE moviecast.movie_id = %s"
            cast = self.execute_query(cast_query, (movie[0],))
            for actor in cast:
                age_at_release = movie[3] - actor[1]
                print(f"- {actor[0]} at age {age_at_release}")

    def get_person_name(self, person_id):
        # Get the name of a person from their ID
        query = "SELECT name FROM people WHERE id = %s"
        result = self.execute_query(query, (person_id,))
        return result[0][0] if result else None
