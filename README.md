# IW4MAdmin Database Parser

#### A Python3 script designed to export your IW4MAdmin database, parsing it into an easily accessible format. While the native `IW4MAdmin\Database\Database.db` is already accessible, navigating its complex relationships, keys, and constraints can be frustrating. This tool simplifies and streamlines the data, offering a more user-friendly view.

## Arguments
```usage: parse_db.py [-h] [-s {ASC,DESC}] [-p PATH] [-o OUTPUT] [-t] [-c]

optional arguments:
  -h, --help            show this help message and exit
  -s {ASC,DESC}, --sort {ASC,DESC}
                        Sort order for the query results (ASC or DESC).
  -p PATH, --path PATH  Path to the IW4MAdmin database file.
  -o OUTPUT, --output OUTPUT
                        Output directory for the parsed database file.
  -t, --time            Time the script's execution.
  -c, --config          Use default config.json for configuration.```

## Instructions
1. Copy the database to a folder and make sure it's named 'Database.db'
2. Copy the script `parse_db.py` into the location of your database's copy
3. Run the script

* This will generate a new database named `Database_parsed.db` with all of the essential information.

## Building

1. Ensure Python3 is installed on your system and added to PATH
2. Run `build.py`

## Examples

- Parse and save the IW4MAdmin Database in its native directory.
   - `python parse_db.py -p "IW4MAdmin\Database\Database.db" -o "IW4MAdmin\Database"`

- Parse the database on the desktop, output to documents, use a config file, time the operation, and sort entries in descending order.
   - `python parse_db.py -c -t -p "C:\Users\User\Desktop\Database.db" -o "C:\Users\User\Documents" -s DESC`

- Use config file and output to a specific folder.
   - `python parse_db.py -p "Database.db" -o "FilteredOutput" -s DESC -c`

- Parse the database with timing
   - `python parse_db.py -t -p "Database.db" -o "TimedOutput"`

- Extract using the config file for the newest/oldest database entries
   - `python parse_db.py -c -p "Database.db" -o "SelectiveOutput" -s DESC -t`