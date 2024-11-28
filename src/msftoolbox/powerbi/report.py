import logging
import json
from zipfile import ZipFile
import shutil

log = logging.getLogger()


class ReportClient:
    """
    A class to extract information from Power BI report files.

    This class provides methods to extract measures, columns, and aggregations from a Power BI report
    file (with a .pbix extension). It reads the report's internal JSON configuration and extracts
    relevant information.

    Attributes:
        path (str): The path where the report files are located.
        name (str): The name of the report file with .pbix extension.
        result (list): A list to store the extracted information.
    """

    def __init__(self, path, name):
        """
        Initializes the ReportExtractor class.

        Args:
            path (str): The path where the report files are located.
            name (str): The name of the report file with pbix extension.
        """
        self.path = path
        self.name = name
        self.result = []

    def extract(self):
        """
        Extracts information from the report file.

        This function extracts information from a report file in a specific format.
        The report file is a ZIP archive containing layout and configuration files.

        The function performs the following steps:
        1. Create a temporary folder based on the report name.
        2. Extract the contents of the report file to the temporary folder.
        3. Load the report layout from the extracted files.
        4. Iterate over the sections of the report layout and extract information from each visual container.
        5. Store the extracted information in a list of fields.
        6. Remove the temporary folder.

        Returns:
            None
        """
        path_folder = f"{self.path}/temp_{self.name[:-5]}"
        try:
            shutil.rmtree(path_folder)
        except FileNotFoundError:
            print(f"folder {path_folder} not present")
        with ZipFile(f"{self.path}/{self.name}", "r") as file:
            file.extractall(path_folder)

        with open(f"{path_folder}/Report/Layout", "r", encoding="utf-16 le") as report_file:
            report_layout = json.loads(
                report_file.read()
            )

        fields = []
        for section in report_layout["sections"]:
            for visual_container in section["visualContainers"]:
                try:
                    query_dict = json.loads(visual_container["config"])
                    for command in query_dict["singleVisual"]["prototypeQuery"]["Select"]:
                        if "Measure" in command.keys():
                            # - MEASURES
                            name = command["Name"].split(".")[1]
                            table = command["Name"].split(".")[0]
                            fields.append([
                                section["displayName"],
                                query_dict["name"],
                                table,
                                name,
                                "Measure"
                                ])

                        elif "Column" in command.keys():
                            # COLUMNS
                            name = command["Name"].split(".")[1]
                            table = command["Name"].split(".")[0]
                            fields.append([
                                section["displayName"],
                                query_dict["name"],
                                table,
                                name,
                                "Column"
                                ])

                        elif "Aggregation" in command.keys():
                            # AGGREGATIONS
                            if ("(" in command["Name"]) & (")" in command["Name"]):
                                txt_extraction = command["Name"][
                                    command["Name"].find("(") + 1 : command["Name"].find(")")
                                ]
                                name = txt_extraction.split(".")[1]
                                table = txt_extraction.split(".")[0]
                                fields.append([
                                    section["displayName"],
                                    query_dict["name"],
                                    table,
                                    name,
                                    "Aggregation"
                                    ])

                except (KeyError, json.JSONDecodeError):
                    pass
        self.result = fields
        shutil.rmtree(path_folder)
