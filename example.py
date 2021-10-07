from src.downloader import XemwayFileDownloader
import logging
logging.getLogger().setLevel(logging.FATAL)

if __name__ == "__main__":
    downloader = XemwayFileDownloader()
    cursor = downloader.get_file_cursor("DELTA_0018")
    print(f"Number of session files {cursor.get_count()}")
    print(cursor.get_item())
    print(cursor.next(20).get_item())
    print(cursor.next().get_item())

    id = cursor.get_item()["_id"]
    downloader.download_file(id, "./test.zip")
