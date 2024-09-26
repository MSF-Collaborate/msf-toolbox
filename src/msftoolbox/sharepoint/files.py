from typing import List
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

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
            keep_metadata (bool): If false returns only the server url, else the full properties object
        Returns:
            List[str]: A list of file names in the folder.
        """
        # Get the folder
        folder = self.context.web.get_folder_by_server_relative_url(
            folder_url
            )

        files = folder.files
        self.context.load(files)
        self.context.execute_query_with_incremental_retry()
        if keep_metadata:
            return [file.properties for file in files]
        else:
            return [file.properties['ServerRelativeUrl'] for file in files]


    def list_folders_in_folder(
        self,
        folder_url: str
        ) -> List[str]:
        """
        Lists all files in a specified folder.

        Args:
            folder_url (str): The server-relative URL of the folder.

        Returns:
            List[str]: A list of file names in the folder.
        """
        # Get the folder
        folder = self.context.web.get_folder_by_server_relative_url(
            folder_url
            )

        folders = folder.folders
        self.context.load(folders)
        self.context.execute_query_with_incremental_retry()
        return [folder.properties['Name'] for folder in folders]

    def download_file(
        self,
        file_url: str,
        download_path: str
        ) -> None:
        """
        Downloads a file from SharePoint.

        Args:
            file_url (str): The server-relative URL of the file.
            download_path (str): The local path where the file will be saved.
        """
        file = self.context.web.get_file_by_server_relative_url(file_url)
        self.context.load(file)
        self.context.execute_query_with_incremental_retry()
        with open(download_path, "wb") as local_file:
            file.download(local_file).execute_query()
        print(f"Downloaded: {download_path}")

    def load_files(
        self,
        folder_url: str
        ) -> List[File]:
        """
        Loads all files in a specified folder.

        Args:
            folder_url (str): The server-relative URL of the folder.

        Returns:
            List[File]: A list of File objects in the folder.
        """
        folder = self.context.web.get_folder_by_server_relative_url(folder_url)
        files = folder.files
        self.context.load(files)
        self.context.execute_query_with_incremental_retry()
        return files

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
        folder = self.context.web.get_folder_by_server_relative_url(folder_url)
        folders = folder.folders
        self.context.load(folders)
        self.context.execute_query_with_incremental_retry()

        # Get all the files in the folder
        all_files = []
        for subfolder in folders:
            subfolder_url = subfolder.properties['ServerRelativeUrl']
            all_files.extend(
                self.recursively_list_files(
                    subfolder_url
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
        folder = (
            self.context.web.ensure_folder_path(folder_url)
            .get()
            .select(["ServerRelativePath"])
            .execute_query()
        )
        return folder.server_relative_path

    # def execute_query_with_incremental_retry(
    #     self
    #     ) -> None:
    #     """
    #     Executes a query with throttling handling.
    #     Retries the request after a delay if throttled.
    #     """
    #     try:
    #         self.context.execute_query()
    #     except Exception as ex:
    #         if "429" in str(ex):
    #             print("Throttled by SharePoint, waiting for 30 seconds...")
    #             time.sleep(30)
    #             self.context.execute_query_with_incremental_retry()
    #         else:
    #             raise ex