from datetime import datetime
from init import MovieDatabase

def main():
    connection_options = {
        "database": "movie",
        "user": "root",
        "host": "localhost",
        "password": "admin",
        "port": 5432
    }
    db = MovieDatabase(connection_options)

    while True:
        command = input('> ')
        parts = command.split()

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

        elif parts[0] == 'a':
            if len(parts) > 1 and parts[1] in ['-p', '-m']:
                if parts[1] == '-p':
                    name = input('Name: ')
                    birth_year = int(input('Birth year: '))
                    # Check if the person already exists
                    if name not in [person['name'] for person in db.people]:
                        db.add_person(name, birth_year)
                    else:
                        print(f'Error: "{name}" already exists in the database. Try again with a different name.')
                elif parts[1] == '-m':
                    title = input('Title: ')
                    length = db.parse_time(input('Length (hh:mm): '))
                    director = input('Director: ')

                    if director not in [person['name'] for person in db.people]:
                        print(f'Error: Director "{director}" not found in the database. Please add the director first.')
                        continue

                    year = int(input('Released in: '))
                    actors = []
                    while True:
                        actor = input('Starring (type "exit" to finish): ')
                        if actor.lower() == 'exit':
                            break
                        if actor not in [person['name'] for person in db.people]:
                            print(f'Error: Actor "{actor}" not found in the database. Please add the actor first.')
                            continue
                        actors.append({'name': actor, 'birth_year': next((person['birth_year'] for person in db.people if person['name'] == actor), None)})
                    db.add_movie(title, length, director, year, actors)
            else:
                print('Error: Incorrect query format. Please check your input.')

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

if __name__ == "__main__":
    main()
