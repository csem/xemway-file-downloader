# Xemway file downloader

The file downloader makes use of 4 environment variables

-   ```XEMWAY_API_ENDPOINT```: Typically https://api.xemway.ch
-   ```XEMWAY_AUTH_ENDPOINT```: Typically https://auth.xemway.ch
-   ```XEMWAY_AUTH_USERNAME```: The Xemway domain concatenated with the username using a colon ":"
-   ```XEMWAY_AUTH_PASSWORD```: Your Xemway password

Those variables must be defined before the downloader is used.

## Example usage

Here is a minimalistic example

```python
from src.downloader import XemwayFileDownloader

if __name__ == "__main__":
    downloader = XemwayFileDownloader()
    cursor = downloader.get_file_cursor("DELTA_0018")
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
    downloader.download_file(id, "./test.zip")
```
