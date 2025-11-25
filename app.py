from db import initialize_database, print_db_location
from login_ui import start_login_ui

if __name__ == "__main__":
    initialize_database()

    print_db_location()
    start_login_ui()