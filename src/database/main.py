from config.init import create_db
from config.initial_data import input_initial_data

if __name__ == "__main__":
    create_db()
    input_initial_data()


    