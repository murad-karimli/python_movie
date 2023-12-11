from datetime import datetime
from init import MovieDatabase



class MovieCLIHandler:
    def __init__(self) -> None:
        self.connection_options = {
            "database": "movie",
            "user": "root",
            "host": "localhost",
            "password": "admin",
            "port": 5432
        }
        self.init_db()

    def init_db(self):
        self.db = MovieDatabase(self.connection_options)
        return self.db

    def delete_person(self, person_name: str):
        person_query = "SELECT id, name FROM People WHERE name = %s"
        person_result = self.db.execute_query(person_query, (person_name,))

        if not person_result:
            print(f"Error: Person '{person_name}' not found in the database.")
            return

        person_id, person_name = person_result[0]

        director_query = "SELECT title FROM movies WHERE director_id = %s"
        director_result = self.db.execute_query(director_query, (person_id,))

        if director_result:
            print(f"Error: Cannot delete '{person_name}' because they are a director in the following movies:")
            for movie_title in director_result:
                print(f"- {movie_title[0]}")
            print("Remove them as a director from these movies first.")
            return

        delete_person_query = "DELETE FROM People WHERE id = %s"
        self.db.execute_query(delete_person_query, (person_id,))

        delete_movie_cast_query = "DELETE FROM MovieCast WHERE actor_id = %s"
        self.db.execute_query(delete_movie_cast_query, (person_id,))

        print(f"Person '{person_name}' and their movie associations deleted successfully.")
           
    def add_movie(self, movie_data, actor_ids):
        title = movie_data.get("title")
        release_year = movie_data.get("release_year")
        length = movie_data.get("length")
        director_id = movie_data.get("director_id")

        existing_movie_query = "SELECT id FROM movies WHERE title = %s AND director_id = %s"
        existing_movie_result = self.db.execute_query(existing_movie_query, (title, director_id))

        if existing_movie_result:
            print(f"Movie '{title}' directed by ID {director_id} already exists.")


        else:
            query = "INSERT INTO movies(title, length, release_year, director_id) VALUES (%s, %s, %s, %s) RETURNING id"
            movie_id = self.db.execute_query(query, (title, length, release_year, director_id), "movies")
            self.add_movie_cast({"movie_id": movie_id, "actor_ids": actor_ids})


    def add_movie_cast(self, data):
        movie_id = data.get("movie_id")
        actor_ids = data.get("actor_ids")
        rows = [(movie_id, actor_id) for actor_id in actor_ids]
        insert_query = "INSERT INTO moviecast (movie_id, actor_id) VALUES (%s, %s)"

        for actor_id in actor_ids:
            self.db.execute_query(insert_query,(movie_id,actor_id),"moviecast")
                


    def parse_time(self, time_str):
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            print('Error: Bad input format (hh:mm), try again!')
            return self.parse_time(input('Length: '))



def main():
    cli_handler = MovieCLIHandler()
    db = cli_handler.init_db()

    while True:
        command = input('> ')
        parts = command.split()

        match command:
            case "a -m":

                title = input("Title: ")
                length = cli_handler.parse_time(input('Length (hh:mm): '))
                director = input('Director: ')

                if not director:
                    print("Error: Director should be provided.")
                    break

                year = int(input('Released in: '))
                actor_ids = []

                director_query = "SELECT id FROM People WHERE name = %s"
                director_id_result = db.execute_query(director_query, (director,))

                if director_id_result:
                    director_id = director_id_result[0][0]
                    print(f"Director ID for '{director}': {director_id}")
                else:
                    print(f"Error: Director '{director}' not found in the database.")
                    break

                while True:
                    actor = input('Starring (type "exit" to finish): ')

                    if not actor or actor.lower() == 'exit':
                        break

                    actor_id_result = db.execute_query("SELECT id FROM People WHERE name = %s", (actor,))
                    print(actor_id_result)
                    if actor_id_result:
                        actor_ids.append(actor_id_result[0][0])
                    else:
                        print(f"Error: Actor '{actor}' not found in the database.")
                        break

                cli_handler.add_movie({"title": title, "release_year": year, "length": length, "director_id": director_id}, actor_ids)

                
                
            case "a -p":
                person_name = input("Name: ")
                birth_year = int(input("Birth year: "))

                existing_person_id_result = db.execute_query("SELECT id FROM People WHERE name = %s", (person_name,))

                if existing_person_id_result:
                    print(f"Error: '{person_name}' already exists in the database. Try again with a different name.")
                else:
                    db.add_person(person_name, birth_year)
                    print(f"Person '{person_name}' added to the database.")

            case "d -p":
                
                name = input('Name: ')
                   
                if name:
                    cli_handler.delete_person(name)
                else:
                    print(f'Error: Person "{name}" not found in the database.')
            
           
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

        elif parts[0] == 'q':
            db.save_data()
            break

        else:
            print('Error: Unknown command. Please check your input.')

main()