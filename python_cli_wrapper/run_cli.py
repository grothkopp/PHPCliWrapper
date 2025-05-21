# python_cli_wrapper/run_cli.py
import os
from cli import Cli # Assuming cli.py is in the same directory or PYTHONPATH
from db_command_base import DbCommandBase # For type hinting or checks if needed
from list_command import ListCommand
from show_command import ShowCommand
from set_command import SetCommand
from db_aware_cd_command import DbAwareCdCommand

def main():
    print("Python CLI Wrapper")
    print("------------------")

    # Database Configuration - User should customize this
    # Consider environment variables for more security
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'your_user'), # Replace with your default or prompt
        'password': os.getenv('DB_PASSWORD', 'your_password'), # Replace with your default or prompt
        'database': os.getenv('DB_NAME', 'test_db') # Replace with your default or prompt
    }

    # Instructions for the user if default credentials are used
    if db_config['user'] == 'your_user' or db_config['password'] == 'your_password':
        print("\nWARNING: Using default placeholder database credentials.")
        print("Please update 'user', 'password', and 'database' in `run_cli.py`")
        print("or set environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.")
        # Decide if you want to proceed or exit
        # proceed = input("Continue with placeholder credentials? (yes/no): ").lower()
        # if proceed != 'yes':
        #     print("Exiting.")
        #     return
        print("Attempting to connect with placeholder credentials...\n")


    # Instantiate the main CLI
    app_cli = Cli()

    # Try to connect to the database and add DB-specific commands
    try:
        # Test connection briefly / Instantiate a base to check
        # This also fetches schema (tables, columns) for all commands.
        # Each command will get its own connection pool entry from mysql.connector by default
        # if they instantiate their own DbCommandBase.
        # To share a single connection, DbCommandBase would need to be instantiated once
        # and passed to commands, or commands would need a get_connection method.
        # For simplicity, let's assume each command manages its own connection via its DbCommandBase parent.
        # This is how PdoCliCommand was used in PHP - one $connection passed to each.
        # Let's refine DbCommandBase and commands to accept a shared connection object.
        # (This will be a modification to existing files)

        # --- Refinement for shared connection (see point 3 below) ---
        # For now, let's proceed with the idea that commands can be initialized
        # and will attempt to connect. If connection fails, they should handle it.
        
        print(f"Connecting to database '{db_config['database']}' on '{db_config['host']}'...")
        # Attempt to create one DbCommandBase to check connection and get schema
        # This schema will be shared by all commands.
        # For now, this is just a pre-flight check. Commands will connect individually.
        shared_db_base_check = DbCommandBase(db_config) # This tries to connect
        
        if not shared_db_base_check.connection:
            print("Failed to establish a database connection. Proceeding without database commands.")
            print("Available commands: exit, history, mark, unmark, go, and basic cd.")
            # Close the connection if it was partially made by shared_db_base_check
            if shared_db_base_check: shared_db_base_check.close()
        else:
            print("Database connection successful. Adding database commands.")
            # Close the pre-flight check connection; commands will make their own.
            shared_db_base_check.close()


            list_cmd = ListCommand(db_config)
            show_cmd = ShowCommand(db_config)
            set_cmd = SetCommand(db_config)
            db_cd_cmd = DbAwareCdCommand(db_config)

            # Check if individual commands connected successfully (optional, they should print errors)
            if not (list_cmd.connection and show_cmd.connection and set_cmd.connection and db_cd_cmd.connection):
                print("Warning: One or more database commands failed to initialize their connection.")
                print("Functionality may be limited.")
                # User can choose to proceed or not.

            app_cli.add_command('list', list_cmd)
            app_cli.add_command('show', show_cmd)
            app_cli.add_command('set', set_cmd)
            app_cli.add_command('cd', db_cd_cmd) # This will override the basic 'cd'

            print("Database commands (list, show, set, context-aware cd) are available.")

    except Exception as e: # Catch any other exception during DB setup
        print(f"An error occurred during database setup: {e}")
        print("Proceeding without database commands.")
        print("Available commands: exit, history, mark, unmark, go, and basic cd.")

    # Run the CLI
    try:
        app_cli.run()
    finally:
        # Ensure any shared resources are cleaned up if we change to shared connection
        # if 'shared_db_base' in locals() and shared_db_base.connection: # 'shared_db_base' was renamed
        #     shared_db_base.close()
        print("CLI exited.")


if __name__ == "__main__":
    main()
