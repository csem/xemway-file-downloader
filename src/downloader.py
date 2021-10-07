import os
import logging
from .cursor import Cursor
from requests import get
from requests.auth import AuthBase, HTTPBasicAuth

logger = logging.getLogger("xemway-file-downloader")


# https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class DeviceSessionCursor(Cursor):

    def __init__(self, device_name: str, bearer_token: str):

        super().__init__()
        self.device_name = device_name
        self.bearer_token = bearer_token
        self.api_endpoint = os.environ["XEMWAY_API_ENDPOINT"]
        self.init()

    def _fetch(self, page: int):
        api_url: str = f"{self.api_endpoint}/api/device/{self.device_name}/files"  # noqa: E501
        logger.info(
            f"Looking for device session files (device: {self.device_name}, page: {page}) at endpoint {api_url}")   # noqa: E501
        result = get(api_url, params={"page": page},
                     auth=BearerAuth(self.bearer_token))
        if result.status_code != 200:
            logger.fatal(
                f"Could not retrieve session files. Server responded with code {result.status_code}")   # noqa: E501
            raise Exception("Could not retrieve session files")
        return result.json()


class BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class XemwayFileDownloader():

    def __init__(self):

        self.auth_endpoint = os.environ["XEMWAY_AUTH_ENDPOINT"]
        self.auth_username = os.environ["XEMWAY_AUTH_USERNAME"]
        self.auth_password = os.environ["XEMWAY_AUTH_PASSWORD"]

        self._bearer_token: str = None

        logging.info(
            f"Performing authentication to { self.auth_endpoint } with username { self.auth_username }")  # noqa: E501

        req_auth = get(f"{self.auth_endpoint}/login", auth=HTTPBasicAuth(
            self.auth_username, self.auth_password))

        if req_auth.status_code != 200:
            logging.fatal('Authorization denied.')
            return

        logging.info("Logged in with success")

        # Store the access token
        self._bearer_token = req_auth.text

    def get_file_cursor(self, device_name: str) -> DeviceSessionCursor:
        return DeviceSessionCursor(device_name, self._bearer_token)

    def download_file(self, session_name: str, save_to_file: str):
        api_endpoint = os.environ["XEMWAY_API_ENDPOINT"]

        api_url: str = f"{api_endpoint}/file/{session_name}/download"

        r = get(api_url, stream=True, auth=BearerAuth(self._bearer_token))
        total_size = int(r.headers["Content-Length"])
        with open(save_to_file, 'wb') as fd:
            current_size = 0
            chunk_size = 128

            print(
                f"Downloading {session_name}.\
                     Total size: {sizeof_fmt(total_size)}")
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
                current_size += chunk_size
                progress = min(100, int(100 * current_size / total_size))

                print(f"Progress: {progress}% [" +
                      "#".join(["" for i in range(progress)]) +
                      "-".join(["" for i in range(100 - progress)]) + "]",
                      end="\r")
        print("")
