from src.cursor import FilterCollection, Filter
from src.downloader import XemwayFileDownloader
import logging

logging.getLogger().setLevel(logging.FATAL)

opts = {
    "extract_archive":
    True,
    "keep_files_containing": [  # keep files containing this string
        "ACC", "ACT", "BARO", "HR",
        "IBI", "TMP",
    ],
}

if __name__ == "__main__":

    with XemwayFileDownloader() as downloader:

        Filter = FilterCollection("and", [
            Filter("session_name", "contains", "20211119"),
        ])

        if downloader.auth_ok:
            cursor = downloader.get_device_file_cursor("DELTA_0018")
            cursor.init(Filter)  # Without filtering, use cursor.init()
            print(f"Number of session files {cursor.get_count()}")
            print(cursor.get_item())
            print(cursor.next(20).get_item())
            print(cursor.next().get_item())

            id = cursor.get_item()["session_name"]
            downloader.download_file(id, "./download", opts)
        else:
            print("Could not log in")