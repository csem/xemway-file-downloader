from src.cursor import FilterCollection, Filter
from src.downloader import XemwayFileDownloader
import logging

logging.getLogger().setLevel(logging.WARNING)

'''
  Notes about opts:
  It is recommended to only use either:
    keep_files_containing
  or
    erase_files_containing

  because even if they are not mutually exclusive, keep_files_containing
  will erase anything not covered by its contents, so erase_files_containing
  may not find the files even if they had existed just before.
'''
opts = {
    "erase_after_extract": False,
    "extract_archive": False,
    "keep_files_containing": [  # keep files containing this string
        "ACC", "ACT", "BARO", "HR",
        "IBI", "TMP",
    ],
    # "erase_files_containing": [  # erase files containing this string
    #     "PPG",
    # ],
}

if __name__ == "__main__":

    with XemwayFileDownloader() as downloader:

        Filter = FilterCollection("and", [
            Filter("session_name", "contains", "20220126"),
        ])

        if downloader.auth_ok:
            cursor = downloader.get_device_file_cursor("DELTA_0085")
            cursor.init(Filter)  # Without filtering, use cursor.init()
            print(f"Number of session files {cursor.get_count()}")
            # input('Get item')
            # print(cursor.get_item())
            # input('Get Next item')
            # print(cursor.next(2).get_item())
            # input('Get Next x2 item')
            # print(cursor.next(2).get_item())

            id = cursor.get_item()["session_name"]
            downloader.download_file(id, f"{id}", opts)
        else:
            print("Could not log in")