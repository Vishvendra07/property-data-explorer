# Property Data Explorer

Filter fictional properties, select a record in a map or a table, and share the chosen filter values through the URL.

[Source](project.py) · [Demo evidence](evidence/demo.html) · [Verification](evidence/checks.json)

## Run locally

Requires Python 3.11+.

```sh
python -m pip install -r requirements.txt
python project.py --html explorer.html
python project.py --district West --maximum 260000 --beds 3
python -m unittest discover -v
```

## Engineering decision

Keep a stable ID across the map and table, use explicit URL filters, and retain the DuckDB query plan beside the browser preview.

The map coordinates are schematic and the data is authored. The live report has a file or static-server entry point and can be used without provider keys.



[Technology or project reference](https://duckdb.org/docs/stable/clients/python/overview)
