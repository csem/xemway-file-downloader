import os
import logging
from .cursor import Cursor
from requests import get
from requests.auth import AuthBase, HTTPBasicAuth
import json
import shutil

logger = logging.getLogger("xemway-file-downloader")

archive_format = "zip"


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

    def _fetch(self, filtering):
        api_url: str = f"{self.api_endpoint}/api/files/device/{self.device_name}"  # noqa: E501
        logger.info(
            f"Looking for device session files (device: {self.device_name}, filter: {filtering}) at endpoint {api_url}"
        )  # noqa: E501
        result = get(api_url,
                     params={"filtering": filtering},
                     auth=BearerAuth(self.bearer_token))

        result_json = result.json()
        if result.status_code != 200:
            logger.fatal(
                f"Could not retrieve session files. Server responded with code {result.status_code}"
            )  # noqa: E501
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
        '''Registers the credentials from environment variables'''
        self.auth_endpoint = os.environ["XEMWAY_AUTH_ENDPOINT"]
        self.auth_username = os.environ["XEMWAY_AUTH_USERNAME"]
        self.auth_password = os.environ["XEMWAY_AUTH_PASSWORD"]
        self.auth_ok = False

    def __enter__(self):
        '''Attempts to log with to the endpoint with the given credentials'''
        self._bearer_token: str = None

        logging.info(
            f"Performing authentication to { self.auth_endpoint } with username { self.auth_username }"
        )  # noqa: E501

        req_auth = get(f"{self.auth_endpoint}/login?appId=xem",
                       auth=HTTPBasicAuth(self.auth_username,
                                          self.auth_password))

        if req_auth.status_code != 200:
            logging.fatal('Authorization denied.')
            return self

        self.auth_ok = True
        logging.info("Logged in with success")
        # Store the access token
        self._bearer_token = req_auth.text
        return self

    def __exit__(self, exc_type, exc_value, trback):
        self._bearer_token = None
        logging.info(
            "Error obtaining a download ressource. Are your credentials correct ?"
        )
        pass

    def get_device_file_cursor(self, device_name: str) -> DeviceSessionCursor:
        '''
        Returns a cursor pointint to a list of files per device

            Parameters
                device_name (str): The name of the device
            
            Returns:
                cursor (DeviceSessionCursor): A cursor to the list of files for this device
        '''
        return DeviceSessionCursor(device_name, self._bearer_token)

    def download_file(self, session_name: str, save_to_file: str, opts: dict):
        '''
        Initiates a file download

            Parameters
                session_name (str): The name of the session to download
                save_to_file (str): The path where the file should be stored, including the filename (usually with .zip)
                opts (dict): Additional options to further specify the download behaviour
                opts.extract_archive (bool): Whether or not to extract the archive (uses shutils)
                opts.keep_files (list): A list of filenames to keep. The other ones will be removed. Use None to keep all files
        '''

        api_endpoint = os.environ["XEMWAY_API_ENDPOINT"]

        api_url: str = f"{api_endpoint}/file/{session_name}/download"
        r = get(api_url, stream=True, auth=BearerAuth(self._bearer_token))
        total_size = int(r.headers["Content-Length"])

        if r.status_code != 200:
            raise Exception("Could not download the file")

        with open(save_to_file, 'wb') as fd:
            current_size = 0
            chunk_size = 128

            print(f"Downloading {session_name}.\
                     Total size: {sizeof_fmt(total_size)}")
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
                current_size += chunk_size
                progress = min(100, int(100 * current_size / total_size))

                print(f"Progress: {progress}% [" +
                      "#".join(["" for i in range(progress)]) +
                      "-".join(["" for i in range(100 - progress)]) + "]",
                      end="\r")

        foldername = "%s_extracted" % (save_to_file)
        if "extract_archive" in opts and opts["extract_archive"]:
            shutil.unpack_archive(save_to_file, foldername, archive_format)

        if "keep_files_containing" in opts:

            with os.scandir(foldername) as it:
                for entry in it:
                    if not entry.name.startswith('.') and entry.is_file():
                        to_be_erased = True
                        for prefix in opts["keep_files_containing"]:
                            if prefix in entry.name:
                                to_be_erased = False

                        if to_be_erased:
                            os.remove(entry.path)

            os.remove(save_to_file)
        print("")
