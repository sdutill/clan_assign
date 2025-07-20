import sys

import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsEditor:
    def __init__(
        self,
        credentials_path: str,
        document_name: str,
    ):
        """
        Initialize the Google Sheets editor

        Args:
            credentials_path: Path to your Google service account JSON file
            document_name: Name of the existing spreadsheet used to track player data
        """

        # Set up Google Sheets authentication
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)

        self.document_name = document_name
        self.gc = gspread.authorize(creds)
        self.sheet = self.gc.open(document_name)
        self.players = self._set_players()

    def _set_players(self, player_list_sheetname: str = "Player List") -> list:
        """
        Set up an existing Google Sheet for clan tracking - parses all player data
        Args:
            player_list_sheetname: Name of the sheet with the list of players
        Returns:
            list of player dictionaries with all available data
        """
        try:
            player_list_sheet = self.sheet.worksheet(player_list_sheetname)

            # Get all data from the worksheet
            all_data = player_list_sheet.get_all_records()

            # Store the parsed data in self.players
            self.players = all_data

        except gspread.WorksheetNotFound as e:
            print(f"Error: Worksheet '{player_list_sheetname}' not found: {e}")
            self.players = []
        except Exception as e:
            print(f"Error parsing player data: {e}")
            self.players = []

        return self.players

    def get_players(self) -> None:
        """
        Returns users to the console

        """
        # Get or create Player List worksheet
        if self.players is None:
            self._set_players()

        return self.players

    def list_players(self) -> None:
        """
        Prints users to the console

        """
        # Get or create Player List worksheet
        if self.players is None:
            self._set_players()

        print(self.players)

    def update_player_data(
        self,
        username: str,
        player_data: dict,
    ):
        """
        Update a single player's data in the sheet - creates a new sheet with user's name
        and populates it with item data

        Args:
            username: Player's username
            player_data: Player's profile data from API
        """
        try:
            print(f"Processing profile data for {username}...")

            # Get items from player data
            items = player_data.get("items", {})
            if not items:
                print(f"No items found for {username}")
                return

            # Create or get worksheet with username
            try:
                worksheet = self.sheet.worksheet(username)
            except gspread.WorksheetNotFound:
                # print(f"Creating new sheet for {username}...")
                print(f"Error: No sheet found for {username}...")
                sys.exit()

            # Start at row 750
            item_data_start = 750
            # Set up headers
            headers = ["name", "id", "quantity"]
            worksheet.update(f"A{item_data_start}:C{item_data_start}", [headers])

            # Prepare data rows
            data_rows = []

            for item in items:
                # Handle each item as a JSON object/dictionary
                name = item.get("name", "")
                item_id = item.get("id", "")
                quantity = item.get("quantity", item.get("count", 0))
                # Lowercase name to more easily support lookup
                data_rows.append([name.lower(), item_id, quantity])
            # Update the sheet with all data at once (more efficient)
            if data_rows:
                data_start_row = (
                    item_data_start + 1
                )  # Data starts one row after headers
                end_row = len(data_rows) + item_data_start  # Last row with data
                worksheet.update(f"A{data_start_row}:C{end_row}", data_rows)
                print(
                    f"✅ Successfully updated {username}'s sheet with {len(data_rows)} items"
                )
            else:
                print(f"No valid item data found for {username}")

        except Exception as e:
            print(f"❌ Error updating {username}: {str(e)}")
            import traceback

            traceback.print_exc()
