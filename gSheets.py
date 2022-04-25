"""Connect to a google sheets instance.

More info here:
https://developers.google.com/sheets/api/quickstart/python

With this you can get and write from a google sheet
and also create a new sheet in a workbook.

You will need a service account credentials file in .json format.
Go here to see how to create one:
https://developers.google.com/workspace/guides/create-credentials#create_credentials_for_a_service_account

USAGE
from gSheets import GoogleSheetsConnector as gs

# Run this to create a new sheet in a given workbook.
gs(CREDS_FILE).create_new_sheet(SHEET_LINK, 'TESTER')

# Run this to read from a given sheet in a workbook.
x = gs(CREDS_FILE).get_from_gsheet(SHEET_LINK, value_render_option='FORMATTED_VALUE')
print(x['values'])
print(x)
print(type(x['values']))
print(type(x))

# Run this to write a dataframe to a given sheet in a workbook.

sheet_range = f"{sheet_name}!R1C1:R{len(data_frame.index) + 1}C{len(data_frame)}"
gs(CREDS_FILE).write_to_gsheet(
    SHEET_LINK,
    table_data = data_frame,
    sheet_range=sheet_range,
    value_input_option = 'USER_ENTERED',
    insert_data_option='OVERWRITE') ## WILL OVEWRITE ENTIRE SHEET

sheet_range = f"{sheet_name}!J1"
gs(CREDS_FILE).write_to_gsheet(
    SHEET_LINK,
    table_data=[[current_date]],
    sheet_range=sheet_range1,
    value_input_option = 'USER_ENTERED',
    insert_data_option='UPDATE_RANGE') ## WILL UPDATE EXISTING CELLS, BEST FOR JUST UPDATING INDIVIDUAL RECORDS

gs(CREDS_FILE).write_to_gsheet(
    SHEET_LINK,
    table_data,
    sheet_range=sheet_range,
    value_input_option = 'USER_ENTERED',
    insert_data_option='INSERT_ROWS') ## WILL APPEND FROM LAST ROW
"""
import json
import pandas as pd

from urllib.parse import urlparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsConnector:
    """This class provides an instance to a Google Sheets connection
    and methods to read and write to a specified Google sheet.
    """
    SCOPE = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
        ] # we can pull from spreadsheet feeds and/or the google drive.

    def __init__(self, cred_path):
        self.cred_path      = cred_path
        self.imposter_email = json.load(open(cred_path))["subject"]
       
    def _create_connection_and_impersonate(self) -> None:
        auth =  ServiceAccountCredentials.from_json_keyfile_name(self.cred_path, self.SCOPE)
        credentials = auth.create_delegated(self.imposter_email)
        # Needs to be v4 to be API version 4 
        service = build('sheets', 'v4', credentials=credentials) 
        return service 
    
    def get_from_gsheet(self, sheet_link:str, **kwargs) -> dict:
        """Pull directly from a specific Google Sheet.
        Returns a dictionary.

        param sheet_link: The hyperlink string to the desired google sheet.
        type sheet_link: string
        param sheet_range: DEFAULT:=Sheet1!A1:ZZ | The desired sheet_name!Range
        of where to pull from ie Sheet1!A15:Z1000
        type sheet_range: string
        param get_option: DEFAULT:=GET | Returns a range of values from a spreadsheet.
        The caller must specify the spreadsheet ID and a range.
        BATCH_GET | Returns one or more ranges of values from a spreadsheet.
        The caller must specify the spreadsheet ID and one or more ranges.
        type get_option: string
        param major_dimension: DEFAULT:=ROWS | Operates on the rows of a sheet.
        COLUMNS | Operates on the columns of a sheet.
        type major_dimension: string
        param value_render_option: DEFAULT:=FORMATTED_VALUE | Values will be calculated &
        formatted in the reply according to the cell's formatting. Formatting is based
        on the spreadsheet's locale, not the requesting user's locale.
        For example, if A1 is 1.23 and A2 is =A1 and formatted as currency,
        then A2 would return "$1.23".
        UNFORMATTED_VALUE: Values will be calculated, but not formatted in the reply.
        For example, if A1 is 1.23 and A2 is =A1 and formatted as
        currency, then A2 would return the number 1.23.
        FORMULA: Values will not be calculated. The reply will include the formulas.
        For example, if A1 is 1.23 and A2 is =A1 and formatted as currency,
        then A2 would return "=A1".
        type value_render_option: string
        param date_time_render_option: DEFAULT=FORMATTED_STRING | Instructs date, time,
        datetime, and duration fields to be output as strings in their given number
        format (which is dependent on the spreadsheet locale).
        SERIAL_NUMBER: Instructs date, time, datetime, and duration fields to be output
        as doubles in "serial number" format, as popularized by Lotus 1-2-3. The whole
        number portion of the value (left of the decimal) counts the days since
        December 30th 1899. The fractional portion (right of the decimal) counts the time
        as a fraction of the day. For example, January 1st 1900 at noon would be 2.5,
        2 because it's 2 days after December 30st 1899, and .5 because noon is half a day.
        February 1st 1900 at 3pm would be 33.625. This correctly treats the year 1900 as not a leap year.
        type date_time_render_option: string
        :rtype: dict
        """
        # initialize the connection
        self.service = self._create_connection_and_impersonate()
        # first, parse the sheet_link string for the sheet id & 
        # return the longest portion of the parsed sheet_link
        sheetId = max(urlparse(sheet_link).path.split('/'), key = len) 

        ## DEFAULT PARAMETERS.
        params = {
            "sheet_range":"Sheet1!A1:ZZ",
            "major_dimension":"ROWS",
            "value_render_option":"FORMATTED_VALUE",
            "date_time_render_option":"FORMATTED_STRING"
            }

        if kwargs:
            params.update({i:kwargs[i] for i in kwargs.keys()})

        # Results will be in json format.
        results = self.service.spreadsheets().values().get(
                        spreadsheetId        = sheetId,
                        range                = params["sheet_range"],
                        majorDimension       = params["major_dimension"],
                        dateTimeRenderOption = params["date_time_render_option"]
                        ).execute()
        if 'values' in results.keys():
            return results
        else:
             print(f'No Values Returned! The range you entered: {params["sheet_range"]} may be blank! Please check that and try again!')

    def write_to_gsheet(self, sheet_link:str, table_data:pd.DataFrame, **kwargs) -> None:
        """Writes to a given google sheet.

        param sheet_link: A string that contains the sheet you wish to update
        type sheet_link: string
        param table_data: A pandas DataFrame object with the data update.
        type table_data: pandas.DataFrame()
        param sheet_range: Default is "Sheet!A1:ZZ" if not specified.
        type sheet_range: string
        param value_input_option: DEFAULT: RAW, The values the user has
        entered will not be parsed and will be stored as-is.
        USER_ENTERED The values will be parsed as if the user typed
        them into the UI. Numbers will stay as numbers, but strings
        may be converted to numbers, dates, etc. following the same
        rules that are applied when entering text into a cell via the 
        Google Sheets UI.
        INPUT_VALUE_OPTION_UNSPECIFIED - Default input value. This value
        must not be used.
        type value_input_option: string
        param insert_data_option: DEFAULT=INSERT_ROWS Rows are inserted
        and the new data is appended.
        UPDATE - Will update an existing cell. If A1 has data, the data within it will be replaced.
        OVERWRITE - All existing data in the sheet will be cleared before new data replaces it.
        type insert_data_option: string
        param major_dimension: DEFAULT=ROWS
        type major_dimension: string
        param date_time_render_option: DEFAULT=FORMATTED_STRING
        type date_time_render_option: string
        """
        # initialize the connection
        self.service = self._create_connection_and_impersonate()
        # parse the sheet_link string for the sheet id 
        sID = max(urlparse(sheet_link).path.split('/'), key = len) # returns the longest portion of the parsed sheet_link

        ## DEFAULT PARAMETERS.
        params = {
            "sheet_range":"Sheet1!A1:ZZ",
            "insert_data_option": "INSERT_ROWS",
            "major_dimension":"ROWS",
            "date_time_render_option":"FORMATTED_STRING"
            }

        if kwargs:
            params.update({i:kwargs[i] for i in kwargs.keys()})

        if isinstance(table_data, pd.DataFrame):
            data = pd.read_json(table_data.to_json()).to_numpy(na_value=None).tolist()
        else:
            data = table_data

        ## OVERWRITE:
        if params["insert_data_option"] == 'OVERWRITE':
            request = self.service.spreadsheets().values().clear(
                                        spreadsheetId    = sID,
                                        range            = params["sheet_range"]
                                        ).execute()
            columns = list(table_data.columns)
            request = self.service.spreadsheets().values().update(
                                        spreadsheetId    = sID,
                                        range            = params["sheet_range"],
                                        valueInputOption = params["value_input_option"],
                                        body             = {"values": [columns] + data}
                                        ).execute()
        ## APPEND
        elif params["insert_data_option"] == 'INSERT_ROWS':
            request = self.service.spreadsheets().values().append(
                                        spreadsheetId    = sID,
                                        range            = params["sheet_range"],
                                        valueInputOption = params["value_input_option"],
                                        insertDataOption = params["insert_data_option"],
                                        body             = {"values": data}
                                        ).execute()
        ## UPDATE
        elif params["insert_data_option"] == 'UPDATE_RANGE':
            request = self.service.spreadsheets().values().update(
                                        spreadsheetId    = sID,
                                        range            = params["sheet_range"],
                                        valueInputOption = params["value_input_option"],
                                        body             = {"values": data}
                                        ).execute()
        else:
            print("Invalid insert data option provided. Only INSERT_ROWS, UPDATE_RANGE & OVERWRITE allowed")

        return request

    def create_new_sheet(self, sheet_link:str, new_sheet_name:str) -> None:
        """Create a new Google Sheet.

        param sheet_link: A string that contains the workbook link
        type sheet_link: string
        param new_sheet_name: The name of the new sheet.
        type new_sheet_name: string
        """
        self.service = self._create_connection_and_impersonate()
        workbook = self.service.spreadsheets()
        sheetId = max(urlparse(sheet_link).path.split('/'), key = len) # return the longest portion of the parsed sheet_link
        data = {        
            'requests': [
            { # add addSheet request
            'addSheet':{ 
                'properties':{'title': new_sheet_name}
                    }
                }
            ]
        }

        req = workbook.batchUpdate(
            spreadsheetId = sheetId,
            body          = data
        )

        try:
            resp = req.execute()
            print(f'{new_sheet_name} has been created!')

        except HttpError as Error:
            er = json.loads(Error.content.decode("utf-8"))
            print(er)
