from datetime import datetime
from init import MovieDatabase

import psycopg2


class MovieCLIHandler:
    def __init__(self) -> None:
        self.init_db()

    def init_db(self):
        connection_options = {
        "database": "movie",
        "user": "root",
        "host": "localhost",
        "password": "admin",
        "port": 5432
        }
        self.db = MovieDatabase(connection_options)

        return self.db
        
    def add_movie(self, movie_data, actor_ids):
        title = movie_data.get("title")
        release_year = movie_data.get("release_year")
        lenght = movie_data.get("length")
        director_id = movie_data.get("director_id")
    
        query = "INSERT INTO movies (title, length, release_year, director_id) VALUES (%s, %s, %s, %s) RETURNING id"
        movie_id = self.db.execute_query(query, title, lenght, release_year, director_id)
        self.add_movie_cast({"movie_id": movie_id, "actor_ids": actor_ids})

    def add_person(self, data: tuple):
        query = "INSERT INTO movies (name, birth_year) VALUES (%s, %s) RETURNING id"
        return self.db.execute_query(query, data)

    def add_movie_cast(self, data):
        movie_id = data.get("movie_id")
        actor_ids = data.get("actor_ids")
        rows = [(movie_id, actor_id) for actor_id in actor_ids]
        # Generate the INSERT INTO ... VALUES statement
        with psycopg2.connect(**self.connection_options) as conn:
            with conn.cursor() as cursor:
                insert_query = "INSERT INTO MovieCast(movie_id, director_id, actor_id) VALUES "
                values_str = ', '.join(cursor.mogrify("(%s, %s)", row).decode('utf-8') for row in rows)
                insert_query += values_str


    def parse_time(self, time_str):
        # Parse the time in HH:MM format
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            print('Error: Bad input format (hh:mm), try again!')
            return self.parse_time(input('Length: '))

def main():
    cli_handler = MovieCLIHandler()
    db = cli_handler.init_db()

    def parse_time(self, time_str):
        # Parse the time in HH:MM format
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            print('Error: Bad input format (hh:mm), try again!')
            return self.parse_time(input('Length: '))  

    while True:
        command = input('> ')
        parts = command.split()

        match command:
            case "a -m":
                title = input("Title: ")
                length = cli_handler.parse_time(input('Length (hh:mm): '))
                director = input('Director: ')

                if not director:
                    print("Error directory should be provided")
                    break
                year = int(input('Released in: '))
                actor_ids = []

                if director_id:= db.execute_query("FIND director"):
                    print("Couldnt find director from database")
                    break

                while True:
                    if not (actor := input('Starring (type "exit" to finish): ')):
                        break

                    if actor.lower() == 'exit':
                        break
                    
                    if actor_id_from_db := db.execute_query("SELECT actors"):
                        actor_ids.append(actor_id_from_db)
                    else:
                        break
                
                    
                cli_handler.add_movie({"title": title, "release_year": year, "length": length, "directory_id": director_id}, actor_ids)
                        

        if not parts:
            continue

        if parts[0] == 'l':
            verbose = '-v' in parts
            title_regex = next((x[3:] for x in parts if x.startswith('-t')), None)
            director_regex = next((x[2:] for x in parts if x.startswith('-d')), None)
            actor_regex = next((x[2:] for x in parts if x.startswith('-a')), None)
            ascending = '-la' in parts
            descending = '-ld' in parts

            if ascending and descending:
                print('Error: Both -la and -ld are present. Please choose one.')
                continue

            if not parts[1:] or parts[1] in ['-v', '-la', '-ld']:
                db.list_movies(verbose, title_regex, director_regex, actor_regex, ascending=not descending)
            else:
                print('Error: Incorrect query format. Please check your input.')


        # elif parts[0] == 'a':
        #     if len(parts) > 1 and parts[1] in ['-p', '-m']:
        #         if parts[1] == '-p':
        #             name = input('Name: ')
        #             birth_year = int(input('Birth year: '))
        #             # Check if the person already exists
        #             if name not in [person['name'] for person in db.people]:
        #                 db.add_person(name, birth_year)
        #             else:
        #                 print(f'Error: "{name}" already exists in the database. Try again with a different name.')
        #         elif parts[1] == '-m':
        #             title = input('Title: ')
        #             length = db.parse_time(input('Length (hh:mm): '))
        #             director = input('Director: ')

        #             if director not in [person['name'] for person in db.people]:
        #                 print(f'Error: Director "{director}" not found in the database. Please add the director first.')
        #                 continue

        #             year = int(input('Released in: '))
        #             actors = []
        #             while True:
        #                 actor = input('Starring (type "exit" to finish): ')
        #                 if actor.lower() == 'exit':
        #                     break
        #                 if actor not in [person['name'] for person in db.people]:
        #                     print(f'Error: Actor "{actor}" not found in the database. Please add the actor first.')
        #                     continue
        #                 actors.append({'name': actor, 'birth_year': next((person['birth_year'] for person in db.people if person['name'] == actor), None)})
        #             db.add_movie(title, length, director, year, actors)
        #     else:
        #         print('Error: Incorrect query format. Please check your input.')

        elif parts[0] == 'd':
            if len(parts) > 1 and parts[1] == '-p':
                name = input('Name: ')
                # Check if the person exists before deleting
                if name in [person['name'] for person in db.people]:
                    db.delete_person(name)
                else:
                    print(f'Error: Person "{name}" not found in the database.')
            else:
                print('Error: Incorrect query format. Please check your input.')

        elif parts[0] == 'q':
            # Save data and exit the program
            db.save_data()
            break

        else:
            print('Error: Unknown command. Please check your input.')

main()