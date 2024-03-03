# IW4MAdmin Database Parser

#### A Python3 script designed to export your IW4MAdmin database, parsing it into an easily accessible format. While the native `IW4MAdmin\Database\Database.db` is already accessible, navigating its complex relationships, keys, and constraints can be frustrating. This tool simplifies and streamlines the data, offering a more user-friendly view.

* Usage: `python parse_db.py`

## Instructions
1. Copy the database to a folder and make sure it's named 'Database.db'
2. Copy the script `parse_db.py` into the location of your database's copy
3. Run the script

* This will generate a new database named `Database_parsed.db` with all of the essential information.

## Building

1. Ensure Python3 is installed on your system and added to PATH
2. Run `build.py`