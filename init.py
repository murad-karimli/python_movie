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

    def execute_query(self, query, params: tuple = None , table_name=None):
        with psycopg2.connect(**self.connection_options) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                if table_name:
                    cursor.execute("SELECT ID FROM " + table_name + " WHERE id = LASTVAL();")
                    return cursor.fetchone()
                conn.commit()


    def check_and_create_tables(self):
        query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'people' OR table_name = 'movies' OR table_name = 'moviecast');"
        result = self.execute_query(query)
        tables_exist = result[0][0]

        if not tables_exist:
            self.run_create_tables_script()

    def run_create_tables_script(self):
        script_path = os.path.join(os.path.dirname(__file__), 'create-tables.bat')
        subprocess.run([script_path])

    def list_movies(self, verbose=False, title_regex=None, director_regex=None, actor_regex=None, ascending=True):
        query = "SELECT * FROM movies"
        if title_regex:
            query += f" WHERE title ~ '{title_regex}'"
        if director_regex:
            query += f" AND director ~ '{director_regex}'"
        if actor_regex:
            query += f" AND EXISTS (SELECT 1 FROM moviecast WHERE movies.id = moviecast.movie_id AND EXISTS (SELECT 1 FROM people WHERE actor_id = moviecast.actor_id AND name ~ '{actor_regex}'))"
        query += f" ORDER BY length {'ASC' if ascending else 'DESC'}, title ASC"
        result = self.execute_query(query)

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


    def get_person_id(self, name):
        query = "SELECT id FROM people WHERE name = %s"
        result = self.execute_query(query, (name,))
        return result[0][0] if result else None

    def print_movie(self, movie, verbose=False):
        print(f"{movie[1]} by {self.get_person_name(movie[2])} in {movie[3]}, {movie[4]}")
        if verbose:
            print('Starring:')
            cast_query = """
            SELECT People.name, People.birth_year
            FROM MovieCast
            JOIN People ON MovieCast.actor_id = People.id
            WHERE MovieCast.movie_id = %s;
        """

            cast = self.execute_query(cast_query, (movie[0],))
            for actor in cast:
                age_at_release = movie[3] - actor[1]
                print(f"- {actor[0]} at age {age_at_release}")

    def get_person_name(self, person_id):
        query = "SELECT name FROM people WHERE id = %s"
        result = self.execute_query(query, (person_id,))
        return result[0][0] if result else None
