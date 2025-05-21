import json
import readline
import os # For marks_file path

class Cli:
    def __init__(self):
        self.prompting = True
        self.path = []
        self.status = 0
        self.history = []
        self.marks = {}
        # Store marks file in user's home directory for better persistence
        self.marks_file = os.path.expanduser("~/.pycli_marks") 
        self.load_marks()
        self.commands = {}
        # 'cd' is now primarily handled by DbAwareCdCommand if registered.
        # 'basic_cd' is the fallback if DbAwareCdCommand is not used.
        self.known_command_names = ["basic_cd", "exit", "history", "mark", "unmark", "go"]
        # Note: 'cd' will be added to known_command_names by add_command if DbAwareCdCommand is registered.
        self.known_command_names.sort() 

    def load_marks(self):
        try:
            with open(self.marks_file, 'r') as f:
                self.marks = json.load(f)
        except FileNotFoundError:
            pass # No marks file yet, that's fine
        except json.JSONDecodeError:
            print(f"Error: Could not decode marks from {self.marks_file}. Starting with empty marks.")
            self.marks = {} # Reset to empty if corrupted

    def save_marks(self):
        try:
            with open(self.marks_file, 'w') as f:
                json.dump(self.marks, f, indent=4) # Add indent for readability
        except IOError:
            print(f"Error: Could not write marks to {self.marks_file}.")

    def get_prompt(self):
        path_str = " / ".join(self.path) if self.path else "/"
        
        # ANSI color codes
        color_red = "\033[31m"
        color_green = "\033[32m"
        color_yellow = "\033[33m"
        color_white = "\033[37m"
        color_reset = "\033[0m"

        sep = ">"
        if self.status == 1:
            color1 = color_green
            sep = "#"
        elif self.status > 1:
            color1 = color_yellow
        elif self.status == 0:
            if len(self.path) > 0:
                color1 = color_red
            else:
                color1 = color_white
        else: # Should not happen, but default to white
            color1 = color_white

        prompt = f"{color1}[{self.status}]{color_reset} {path_str} {color_white}{sep}{color_reset} "
        return prompt

    def cmd_basic_cd(self, args: list): # Renamed from cmd_cd
        if not args or args[0] == '.':
            # No-op
            self.status = 0
            return self.status
        elif args[0] == "..":
            if self.path:
                self.path.pop()
        elif args[0] == "/":
            self.path = []
        else:
            full_arg = " ".join(args)
            if full_arg == "/": # Handles "cd /" case if passed as full_arg
                self.path = []
            else:
                new_path_parts = [part.strip() for part in full_arg.split('/') if part.strip()]
                if full_arg.startswith('/'): 
                    self.path = new_path_parts
                else: 
                    self.path.extend(new_path_parts)
        self.status = 0 
        return self.status # Ensure all built-in commands return status

    def cmd_history(self, args: list):
        for item in self.history:
            print(item)
        self.status = 0
        return self.status

    def cmd_mark(self, args: list):
        if len(args) > 0:
            name = args[0]
            self.marks[name] = {"path": list(self.path)} # Store a copy
            self.save_marks()
            print(f"Mark '{name}' set to {'/' + '/'.join(self.path) if self.path else '/'}")
        else:
            if not self.marks:
                print("No marks set.")
                self.status = 0 # No error, just no marks
                return self.status
            print("Current marks:")
            for name, data in self.marks.items():
                path_str = '/' + '/'.join(data['path']) if data['path'] else '/'
                print(f"  {name}: {path_str}")
        self.status = 0
        return self.status

    def cmd_unmark(self, args: list):
        if len(args) > 0 and args[0] in self.marks:
            name_to_delete = args[0]
            del self.marks[name_to_delete]
            self.save_marks()
            print(f"Mark '{name_to_delete}' removed.")
        else:
            print("Mark not found or no name given.")
            self.status = 1 # Indicate error: mark not found
            return self.status
        self.status = 0
        return self.status
    
    def cmd_go(self, args: list):
        if len(args) > 0 and args[0] in self.marks:
            mark_name = args[0]
            self.path = list(self.marks[mark_name]["path"]) # Restore a copy
            path_str = '/' + '/'.join(self.path) if self.path else '/'
            print(f"Path set to: {path_str}")
        else:
            print("Mark not found.")
            self.status = 1 # Error: mark not found
            return self.status
        self.status = 0
        return self.status

    def completer(self, text, state):
        line_buffer = readline.get_line_buffer().lstrip() # Remove leading spaces
        parts = line_buffer.split()
        command_name_typed = ""
        if parts:
            command_name_typed = parts[0]

        # If typing the command name itself
        if not parts or (len(parts) == 1 and not line_buffer.endswith(" ")):
            # `text` will be the partial command name, e.g., "ma" for "mark"
            # `self.known_command_names` includes built-ins and registered commands.
            options = [cmd for cmd in self.known_command_names if cmd.startswith(text)]
            if state < len(options):
                return options[state]
            return None

        # If command name is typed and space follows, try command-specific completion
        if command_name_typed in self.commands:
            cmd_obj = self.commands[command_name_typed]
            if hasattr(cmd_obj, 'complete'):
                # `text` is the current word being completed (e.g. an argument)
                # `parts[1:]` are the arguments already typed
                # However, the completer in DbAwareCdCommand expects `args` to be the full line for `cd`
                # For `cd`, `text` is part of `args[0]`
                # For other commands, `text` is a new arg.
                
                args_for_completer = parts[1:]
                # If the current word `text` is what we are completing, it might not be in parts[1:] yet
                # if it's a new argument. If it is part of an existing argument (e.g. "cd users/somepa"),
                # then text is "somepa" and args_for_completer is ["users/somepa"]
                
                # This logic needs to be robust. `text` is the word to complete.
                # `parts` are the words on the line.
                # If `text` is the last part of `parts`, then `args_for_completer` should exclude it.
                # If `line_buffer.endswith(" ")` is true, text is empty and it's a new arg.

                current_arg_index = len(parts) -1 # Index of the current word being typed
                if line_buffer.endswith(" "): # If space after last typed word, completing a new word
                    current_arg_index += 1
                
                # `text` is the current partial word. `parts` includes that partial word if not empty.
                # For command-specific completers, they usually expect:
                # current_path, all_args_list, current_word_to_complete
                args_list = parts[1:] # All arguments so far

                # The `text` parameter to `completer` is the `current_word`
                # The `state` is for readline to iterate through suggestions
                # `args_list` should contain all typed arguments up to, but not necessarily including, `text`.
                # Let's adjust based on how `ListCommand.complete` and `DbAwareCdCommand.complete` are structured.
                # `ListCommand.complete(self, current_path: list, args: list, current_word: str)`
                #   `args` are existing full args, `current_word` is the one being typed.
                # `DbAwareCdCommand.complete(self, current_path: list, args: list, current_word: str)`
                #   `args` is `line_buffer.split()` (i.e. parts), `current_word` is the one being typed.

                if command_name_typed == 'cd': # DbAwareCdCommand expects different args for complete
                    # It expects args to be the arguments to 'cd' command itself.
                    # e.g. "cd users/em", parts=["cd", "users/em"], text="em" (if completing "users/em")
                    # or text="users/em" (if it's the first arg to cd)
                    # The `DbAwareCdCommand.complete` takes `args` as `line_buffer.split()` from "cd"
                    # and `current_word` as the word being completed.
                    # So, `parts[1:]` (args to cd) and `text` (current word)
                    options = cmd_obj.complete(self.path, parts[1:], text) # Pass cli.path
                elif command_name_typed in ["go", "unmark", "mark"]: # These use simple text for completion against marks or for new mark name
                     pass # Will be handled by generic mark completion below
                elif hasattr(cmd_obj, 'complete'): # For ListCommand, SetCommand, ShowCommand
                    # These expect args already typed, and current_word (text)
                    typed_args = parts[1:]
                    if text in typed_args : # if current_word is already a full part of typed_args
                        # This happens if we are completing an existing argument by pressing tab mid-word.
                        # Example: list some_col<TAB> -> text=some_col, typed_args=["list", "some_col"]
                        # The completer should get args *before* current_word.
                         idx = typed_args.index(text)
                         options = cmd_obj.complete(self.path, typed_args[:idx], text)
                    else: # Completing a new argument or the first part of it
                         options = cmd_obj.complete(self.path, typed_args, text)


                if options and state < len(options):
                    return options[state]
                # Fall through if command-specific completer returns None or no options for this state

        # Generic completion for mark-related commands if not handled by specific completer
        if command_name_typed == "go" or command_name_typed == "unmark":
            if len(parts) == 2: # Completing the mark name
                options = [m for m in self.marks if m.startswith(text)]
                if state < len(options):
                    return options[state]
        
        # Path completion for mark command (e.g. "mark mymark /path/to")
        # This is more complex, similar to cd path completion, skip for now to keep it simple.

        return None # No further completions found

    def add_command(self, name, command_obj):
        self.commands[name] = command_obj
        # Ensure 'cd' (from DbAwareCdCommand) is preferred in completions if it exists
        if name == 'cd' and 'basic_cd' in self.known_command_names:
            self.known_command_names.remove('basic_cd')
        
        if name not in self.known_command_names:
            self.known_command_names.append(name)
            self.known_command_names.sort()


    def run(self):
        # print("Python CLI Wrapper started. Type 'exit' to quit.") # Moved to run_cli.py
        
        
        self.history_file = os.path.expanduser("~/.pycli_history") # Make it an instance var
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass 
        
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")
        # readline.set_completer_delims(" \t\n;") # Optional: refine delimiters

        try: # Main loop and exit handling
            while self.prompting:
                try:
                    line = input(self.get_prompt())
                    raw_line = line.strip()
                    if not raw_line: # Empty line
                        self.status = 0
                        continue

                    self.history.append(raw_line)
                    readline.add_history(raw_line)
                    
                    parts = raw_line.split()
                    command_name = parts[0]
                    command_args = parts[1:]

                    final_command_to_execute = command_name
                    final_args = command_args
                    
                    try:
                        if command_name == "exit":
                            self.prompting = False
                            self.status = 0
                        elif command_name in self.commands: # Registered (list, show, set, db_cd)
                            cmd_obj = self.commands[command_name]
                            self.status = cmd_obj.command(self.path, final_args)
                        elif hasattr(self, f"cmd_{command_name}"): # Built-in (history, mark, unmark, go, basic_cd)
                            method = getattr(self, f"cmd_{command_name}")
                            self.status = method(final_args) # Expect built-ins to return status
                        else: # Unknown command - default to 'cd' logic
                            final_command_to_execute = 'cd' # The actual 'cd' command string
                            final_args = parts # Pass ["unknown_cmd", "arg1"] to 'cd'
                            
                            if final_command_to_execute in self.commands: # DbAwareCdCommand as 'cd'
                                cmd_obj = self.commands[final_command_to_execute]
                                self.status = cmd_obj.command(self.path, final_args)
                            elif hasattr(self, "cmd_basic_cd"): # Fallback to basic_cd if no DbAware 'cd'
                                # print(f"Unknown command, defaulting to basic_cd with args: {final_args}")
                                self.status = self.cmd_basic_cd(final_args)
                            else: # No 'cd' or 'basic_cd' available
                                print(f"Unknown command: {command_name}")
                                self.status = 127 # Command not found status
                    except Exception as e:
                        print(f"Error during command execution '{command_name}': {e}")
                        self.status = 1 # General error status

                except EOFError: 
                    self.prompting = False
                    print("\nExiting (EOF).") 
                    self.status = 0
                except KeyboardInterrupt: 
                    print("\nInterrupted. Type 'exit' to quit.")
                    self.status = 130 
                    # Clear the current input line (optional, might need more robust handling)
                    # readline.set_startup_hook(lambda: readline.insert_text("")) 
                    # readline.set_startup_hook(None)
        finally: # Ensure history is written on exit
            # print("Exiting CLI.run()...") # For debugging
            try:
                readline.write_history_file(self.history_file)
            except Exception as e:
                print(f"Error writing history file: {e}")

if __name__ == "__main__":
    # This basic execution is primarily for testing cli.py itself.
    # run_cli.py is the main entry point for the full application.
    print("Running basic Cli test (no DB commands by default)...")
    test_cli = Cli()
    
    # Example of adding a dummy command for testing completer with registered commands
    class DummyCmd:
        def command(self, path, args): print(f"DummyCmd called with path {path}, args {args}"); return 0
        def complete(self, path, args, current_word): return [f"dummy_sugg_{current_word}"]
    test_cli.add_command("dummy", DummyCmd())
    
    test_cli.run()
