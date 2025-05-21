# python_cli_wrapper/list_command.py
from .db_command_base import DbCommandBase
from .cli_helper import pretty_print 

class ListCommand(DbCommandBase):
    def __init__(self, db_config: dict):
        super().__init__(db_config)

    def command(self, current_path: list, args: list) -> int:
        if not self.connection:
            print("Error: No database connection.")
            return 1
        
        if not current_path:
            print("Error: No table selected. Use 'cd tablename'.")
            return 1

        table_name = current_path[0]
        if table_name not in self.tables:
            print(f"Error: Table '{table_name}' not found.")
            return 1

        columns_to_select_names = []
        if args:
            for arg_col in args:
                if arg_col in self.columns.get(table_name, []):
                    columns_to_select_names.append(arg_col)
                else:
                    print(f"Warning: Column '{arg_col}' not found in table '{table_name}'. Ignoring.")
        else:
            available_cols = self.columns.get(table_name, [])
            columns_to_select_names = available_cols[:5]

        if not columns_to_select_names:
            print(f"Error: No valid columns to display for table '{table_name}'.")
            return 1

        # Use backticks for column names in the query string
        query_cols_str = ", ".join([f"`{col}`" for col in columns_to_select_names])
        
        conditions = current_path[1:]
        where_clause = ""
        if conditions:
            # WARNING: Direct use of path elements in WHERE can be an SQL injection risk.
            # This part assumes conditions are well-formed SQL like "col_name='value'"
            # or "col_name > 10". Proper parameterization is advised for dynamic values.
            where_clause = " WHERE " + " AND ".join(conditions)

        query = f"SELECT {query_cols_str} FROM `{table_name}`{where_clause}"
        
        results = self.execute_query(query)

        if results is None:
            return 1 
        
        if not results:
            print(f"No results found in table '{table_name}'{where_clause}.")
            return 0

        string_results = []
        for row_dict in results:
            str_row = {}
            for col_name in columns_to_select_names: # Ensure order and presence of selected columns
                val = row_dict.get(col_name)
                if isinstance(val, bytes): 
                    try:
                        str_row[col_name] = val.decode('utf-8')
                    except UnicodeDecodeError:
                        str_row[col_name] = '[blob]'
                else:
                     str_row[col_name] = str(val) if val is not None else ""
            string_results.append(str_row)

        pretty_print(string_results)
        return 0 

    def complete(self, current_path: list, args: list, current_word: str) -> list:
        if not current_path:
            return [] 

        table_name = current_path[0]
        if table_name in self.columns:
            possible_columns = self.columns[table_name]
            suggestions = [
                col for col in possible_columns 
                if col.startswith(current_word) and col not in args
            ]
            return suggestions
        return []
