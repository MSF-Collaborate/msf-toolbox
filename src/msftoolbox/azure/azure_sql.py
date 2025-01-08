from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from azure.identity import AzureCliCredential, ManagedIdentityCredential, DefaultAzureCredential
import pandas as pd
import struct
import urllib
import pyodbc

class AzureSQLClient:
    """
    A class to interact with an Azure SQL Database.

    This class provides methods to connect to an Azure SQL Database and execute SQL queries.
    """

    def __init__(self, sqlserver: str, database: str, use_azure_identity: bool = True, local_run: bool = True, managed_identity_client_id: str = None):
        """
        Initialize the AzureSQLClient with server and database details.

        Args:
            sqlserver (str): The name of the SQL Server hosting the database.
            database (str): The name of the database to connect to.
            use_azure_identity (bool): Flag to determine if Azure Identity should be used.
            local_run (bool): Flag to determine if running locally or in production.
            managed_identity_client_id (str): The managed_identity_client_id required for ManagedIdentityCredentials.
        """
        self.sqlserver = sqlserver
        self.database = database
        self.use_azure_identity = use_azure_identity
        self.local_run = local_run
        self.managed_identity_client_id = managed_identity_client_id
        self.credential = self._get_credential() if use_azure_identity else None
        self.engine = None

    def _get_credential(self):
        """
        Determine the credential type based on the local_run flag.

        Returns:
            credential (object): The credentials to be used for authentication.
        """
        if self.local_run:
            return AzureCliCredential()
        elif self.managed_identity_client_id is not None:
            return ManagedIdentityCredential(client_id=self.managed_identity_client_id)
        else:
            return DefaultAzureCredential()

    def connect_with_user_credentials(self, username: str = None, password: str = None) -> Engine:
        """
        Connect to an Azure SQL database using user credentials or Azure Identity if enabled.

        Args:
            username (str): The username to use when connecting to the database.
            password (str): The password to use when connecting to the database.

        Returns:
            Engine: A SQLAlchemy engine object representing the connection to the database.
        """
        if self.use_azure_identity:
            return self.connect_with_cli_credentials()

        if not username or not password:
            raise ValueError("Username and password must be provided when Azure Identity is not used.")

        driver = "{ODBC Driver 17 for SQL Server}"
        serverfqdn = self.sqlserver + ".database.windows.net"
        connectionparams = urllib.parse.quote_plus(
            "Driver=%s;" % driver
            + "Server=tcp:%s,1433;" % serverfqdn
            + "Database=%s;" % self.database
            + "Uid=%s;" % username
            + "Pwd={%s};" % password
            + "Encrypt=yes;"
            + "TrustServerCertificate=no;"
            + "Connection Timeout=30;"
        )
        conn_str = f"mssql+pyodbc:///?odbc_connect={connectionparams}"
        self.engine = create_engine(conn_str, fast_executemany=True)

        # Fail early by executing a simple query
        self._test_connection()

    def connect_with_cli_credentials(self) -> Engine:
        """
        Connect to an Azure SQL database using CLI credentials.

        Returns:
            Engine: A SQLAlchemy engine object representing the connection to the database.
        """
        if not self.use_azure_identity:
            raise ValueError("Azure Identity is not enabled. Use user credentials instead.")

        database_token = self.credential.get_token("https://database.windows.net/")
        tokenb = bytes(database_token.token, "UTF-8")
        exptoken = b''.join(bytes({i}) + bytes(1) for i in tokenb)
        tokenstruct = struct.pack("=i", len(exptoken)) + exptoken

        driver = "Driver={ODBC Driver 17 for SQL Server}"
        server = f";SERVER={self.sqlserver}.database.windows.net"
        database = f";DATABASE={self.database}"
        encryption = ";ENCRYPT=Yes"
        conn_str = driver + server + database + encryption
        params = urllib.parse.quote(conn_str)
        SQL_COPT_SS_ACCESS_TOKEN = 1256

        conn_str = f"mssql+pyodbc:///?odbc_connect={params}"

        self.engine = create_engine(conn_str, connect_args={"attrs_before": {SQL_COPT_SS_ACCESS_TOKEN: tokenstruct}})
        
        # Fail early by executing a simple query
        self._test_connection()

    def _test_connection(self):
        """
        Test the database connection by executing a simple query.

        Raises:
            Exception: If the test query fails, an exception will be raised.
        """
        try:
            self.execute_query("SELECT 1")
        except Exception as e:
            raise ConnectionError(f"Failed to establish a connection to the database: {e}")

    def get_data(self, sql_query: str, params: tuple = None) -> pd.DataFrame:
        """
        Executes a SQL query on a database engine with optional parameters and returns the result as a pandas DataFrame.
        Use this method to return data from the SQL Database.
        For instance: SELECT, EXEC (for stored procedures that do not return data)

        Args:
            sql_query (str): The SQL query to execute.
            params (tuple or list): (optional) The parameters to be passed to the query.

        Returns:
            pandas.DataFrame: A DataFrame containing the result of the SQL query.
        """
        with self.engine.connect() as conn:
            sql_query = text(sql_query)
            if params is not None:
                df_data = pd.read_sql_query(sql_query, conn, params=params)
            else:
                df_data = pd.read_sql_query(sql_query, conn)
        return df_data

    def execute_query(self, sql_query: str) -> None:
        """
        Executes a SQL query on a database engine with no return value.
        Use this method to execute statements that do not return rows of data.
        For instance: CREATE, DROP, EXEC (for stored procedures that do not return data),
        INSERT, GRANT, REVOKE, DELETE, TRUNCATE.

        Args:
            sql_query (str): The SQL query to execute.

        Returns:
            None
        """
        with self.engine.connect() as conn:
            conn.execute(text(sql_query))
            conn.commit()