# Xemway file downloader

The file downloader makes use of 4 environment variables

- `XEMWAY_API_ENDPOINT`: Typically https://api.xemway.ch
- `XEMWAY_AUTH_ENDPOINT`: Typically https://auth.xemway.ch
- `XEMWAY_AUTH_USERNAME`: The Xemway domain concatenated with the username using a colon ":"
- `XEMWAY_AUTH_PASSWORD`: Your Xemway password

Those variables must be defined before the downloader is used.

## Example usage

Here is a minimalistic example.
Check example.py to extract only a subset of the files contained into the archive

```python
from src.downloader import XemwayFileDownloader

if __name__ == "__main__":

    # Acquire a new downloader and attempt a log-in
    with XemwayFileDownloader() as downloader:

        if downloader.auth_ok:
            cursor = downloader.get_file_cursor("DELTA_0018")

            # Initialize the cursor
            cursor.init()

            print(f"Number of session files {cursor.get_count()}")

            # Find the first session (index 0)
            print(cursor.get_item())

            # Move by 20 items and get session (index 20)
            print(cursor.next(20).get_item())

            # Move by 1 item and get the session
            print(cursor.next().get_item())

            # Find out the ID of the session
            id = cursor.get_item()["_id"]

            # Ask the downloader to fetch the file into test.zip
            downloader.download_file(id, "./test.zip", {})

        else:
            print("Could not log in")


```

### Adding custom filters

Our backend supports to some extend nested filtering. You can specify filters in the cursor initialization as such:

```python3
Filter = FilterCollection(
    "and" # can also use "or",
    [
        Filter( column_name, operator, value),
    ]
)

cursor.init(Filter)
```

where `operator` can be `eq`, `isnull`, `isnotnull`, `gte`, `gt`, `lte`, `lt`, `startswith`, `endswith`, `contains`, `doesnotcontain`. Multiple filters can be added to the list, and nesting is possible:

```python3
Filter = FilterCollection(
    "and" # can also use "or",
    [
        Filter( col1, "eq", value),
        FilterCollection(
            "or",
            [
                Filter( col2, "eq", value),
                Filter( col3, "eq", value)
            ]
        )
    ]
)

cursor.init(Filter)
```
