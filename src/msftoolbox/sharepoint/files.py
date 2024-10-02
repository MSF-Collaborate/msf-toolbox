from typing import List
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import os

class SharePointClient:
    """
    A class to interact with the Office365 Sharepoint API.

    This class provides methods to authenticate and interact with the Office365 Sharepoint API, including
    listing files, downloading files and loading files.

    """
    def __init__(
        self,
        site_url: str,
        username: str,
        password: str
        ):
        """
        Initializes the SharePointClient with site URL and user credentials.

        Args:
            site_url (str): The URL of the SharePoint site.
            username (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.site_url = site_url

        self.credentials = UserCredential(
            username,
            password
            )

        self.context = ClientContext(
            site_url
            ).with_credentials(self.credentials)

    def list_files_in_folder(
        self,
        folder_url: str,
        keep_metadata: bool = False
        ) -> List[str]:
        """
        Lists all files in a specified folder.

        Args:
            folder_url (str): The server-relative URL of the folder.
            keep_metadata (bool): If false returns only the name and server url, else the full properties object
        Returns:
            List[dict]: A list of file records in the folder.
        """
        # Get the folder
        folder = self.context.web.get_folder_by_server_relative_url(
            folder_url
            )

        # List the files in the folder
        files = folder.files
        self.context.load(files)
        self.context.execute_query_with_incremental_retry()

        # If the keep_metadata attribute is True then keep
        # all properties else subset for commonly used ones
        if keep_metadata:
            records = [
                file.properties for file in files
                ]
        else:
            records = [{
                field: file.properties[field]
                for field in [
                    "Name",
                    "ServerRelativeUrl",
                    "TimeLastModified"
                    ]
                } for file in files]
        
        return records


    def list_folders_in_folder(
        self,
        folder_url: str,
        keep_metadata: bool = False
        ) -> List[str]:
        """
        Lists all files in a specified folder.

        Args:
            folder_url (str): The server-relative URL of the folder.
            keep_metadata (bool): If false returns only the name and server url, else the full properties object

        Returns:
            List[dict]: A list of folder records in the folder.
        """
        # Get the folder
        folder = self.context.web.get_folder_by_server_relative_url(
            folder_url
            )

        # List folders in the folder
        folders = folder.folders
        self.context.load(folders)
        self.context.execute_query_with_incremental_retry()

        # If the keep_metadata attribute is True then keep
        # all properties else subset for commonly used ones
        if keep_metadata:
            records = [
                folder.properties for folder in folders
                ]
        else:
            records = [{
                field: folder.properties[field]
                for field in [
                    "Name",
                    "ServerRelativeUrl",
                    "TimeLastModified"
                    ]
                } for folder in folders]

        return records

    def download_file(
        self,
        source_url: str,
        destination_file_path: str
        ) -> None:
        """
        Downloads a file from SharePoint.

        Args:
            source_url (str): The server-relative URL of the file.
            local_file_path (str): The local path where the file will be saved.
        """
        # Get the file
        file = self.context.web.get_file_by_server_relative_url(
            source_url
            )

        self.context.load(file)
        self.context.execute_query_with_incremental_retry()

        # Load the file to the local file path
        with open(destination_file_path, "wb") as local_file:
            file.download(
                local_file
                ).execute_query_with_incremental_retry()

        print(f"Downloaded: {destination_file_path}")
        return None

    def upload_file(
        self,
        source_file_path: str,
        destination_url: str
        ) -> None:
        """
        Uploads a file to the sharepoint folder.
        Files up to 4MB are accepted.

        Args:
            source_file_path (str): The local path of the file too upload.
            destination_url (str): The server-relative URL of the folder destination.
        """
        # Open the file and store the content
        with open(source_file_path, "rb") as content_file:
            file_content = content_file.read()

        folder_exists = self.test_folder_existence(
            destination_url
            )

        if not folder_exists:
            raise Exception("The destination folder does not exist")
        else:
            # Get the Sharepoint target folder
            target_folder = self.context.web.get_folder_by_server_relative_url(
                destination_url
                )
            target_folder.get()
            target_folder.execute_query_with_incremental_retry()

            # Get the file name based on the source name
            name = os.path.basename(
                source_file_path
                )

            # Upload
            target_folder.upload_file(
                name,
                file_content
                ).execute_query_with_incremental_retry()

            return None

    def recursively_list_files(
        self,
        folder_url: str,
        keep_metadata: bool = False
        ) -> List[str]:
        """
        Recursively expands folders and lists all files.

        Args:
            folder_url (str): The server-relative URL of the starting folder.
            keep_metadata (bool): If false returns only the server url, else the full properties object

        Returns:
            List[str]: A list of all file names in the folder and its subfolders.
        """
        # Get the folders in the root folder
        folders = self.list_folders_in_folder(
            folder_url
            )

        # Get all the files in the folder
        all_files = []
        for subfolder in folders:
            subfolder_url = subfolder["ServerRelativeUrl"]
            all_files.extend(
                self.recursively_list_files(
                    subfolder_url,
                    keep_metadata
                    )
                )

        all_files.extend(
            self.list_files_in_folder(
                folder_url,
                keep_metadata
                )
            )

        return all_files

    def create_folder_if_not_exists(
        self,
        folder_url
        ):
        """Creates a folder if it does not exist at the specified server-relative URL.

        Args:
            folder_url (str): The server-relative URL of the starting folder.

        Returns:
            str: The server-relative URL of the starting folder.
        """
        folder_test = self.test_folder_existence(folder_url)

        if folder_test:
            print("Folder exits already.")
        else:
            print("Creating folder.")

            folder_test = (
                self.context.web.ensure_folder_path(folder_url)
                .get()
                .select(["ServerRelativePath"])
                .execute_query_with_incremental_retry()
            )
        return None


    def test_folder_existence(
        self,
        folder_url
        ):
        """Tests for the existence of a folder at the server-relative URL.

        Args:
            folder_url (str): The server-relative URL of the starting folder.

        Returns:
            str: The server-relative URL of the starting folder.
        """
        folder_test = (
            self.context.web.get_folder_by_server_relative_path(folder_url)
            .get()
            .execute_query_with_incremental_retry()
            )

        folder_test = folder_test.properties.get("Exists", False)
        return folder_test