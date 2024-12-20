# gpsmap

This project parses GPX files (from [GPSLogger](https://gpslogger.app/) in my case)
into a SQLite database, and then plots that data as dots on a map.

This is solely a personal project and you will need to modify it before using, for
example the file paths and map location are hardcoded.

## Usage

This project is managed with [uv](https://docs.astral.sh/uv/) because it is the best.
Run scripts with `uv run <script>`.

`make_db.py` creates the SQLite database, and `make_map.py` reads from the database and outputs `map.jpg`.

If you run `make_map.py nocache` that will disable using the cached map data which is slower but
required if you change what map components are downloaded. It is also of course required for the
first run, as there is no cache to start with.

## License

This code is licensed under the MIT license.
