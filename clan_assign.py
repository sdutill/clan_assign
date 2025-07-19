import argparse
import json

from lib.google_sheets_editor import GoogleSheetsEditor
from lib.rune_profille_api import RuneProfileAPI


def create_parser():
    parser = argparse.ArgumentParser(
        description="Player data management system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list "document_name"         # Get all player names
  %(prog)s get "milkdud"                # Fetch a specific player's data
  %(prog)s get "milkdud" -o data.json   # Fetch and save to JSON file
  %(prog)s update "doc" "milkdud"       # Update a specific player's data
  %(prog)s update "doc" --all           # Update all players in document
        """,
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Fetch player data command
    get_parser = subparsers.add_parser("get", help="Fetch a player's data")
    get_parser.add_argument("player_name", help="Name of the player to fetch data for")
    get_parser.add_argument(
        "--output", "-o", help="Output file path to save player data as JSON"
    )

    # List player names command
    list_parser = subparsers.add_parser("list", help="Get all player names")
    list_parser.add_argument(
        "document_name",
        help="Name of the Google Sheets document used to store player data",
    )

    # Update player data command
    update_parser = subparsers.add_parser("update", help="Update player data")
    update_parser.add_argument(
        "document_name",
        help="Name of the Google Sheets document used to store player data",
    )

    # Create mutually exclusive group for player_name and --all flag
    update_group = update_parser.add_mutually_exclusive_group(required=True)
    update_group.add_argument(
        "player_name", nargs="?", help="Name of the specific player to update"
    )
    update_group.add_argument(
        "--all", action="store_true", help="Update all players in the document"
    )

    return parser


# Main function to handle control flow
def main():
    parser = create_parser()
    args = parser.parse_args()

    # Initialize api & sheets_document
    api = RuneProfileAPI("https://api.runeprofile.com")

    # Handle the different commands
    if args.command == "list":
        print(f"Getting all player names from document: {args.document_name}")
        rune_document = GoogleSheetsEditor(
            "./service-account-key.json", args.document_name
        )
        rune_document.list_players()

    elif args.command == "get":
        print(f"Fetching data for player: {args.player_name}")
        player_data = api.get_profile(args.player_name)

        if args.output:
            print(f"Saving player data to: {args.output}")
            with open(args.output, "w", encoding="utf8") as json_file:
                json.dump(player_data, json_file, indent=2)
        else:
            print(player_data)

    elif args.command == "update":
        rune_document = GoogleSheetsEditor(
            "./service-account-key.json", args.document_name
        )

        if args.all:
            print(f"Updating all players in document: {args.document_name}")
            # Get all players from the document
            for player in rune_document.players:
                player_name = player.get("Player")
                if player_name:
                    print(f"  Updating player: {player_name}")
                    try:
                        player_data = api.get_profile(player_name)
                        rune_document.update_player_data(player_name, player_data)
                    except Exception as e:
                        print(f"    Error updating {player_name}: {e}")
        else:
            print(
                f"Updating player: {args.player_name} in document: {args.document_name}"
            )
            try:
                player_data = api.get_profile(args.player_name)
                rune_document.update_player_data(args.player_name, player_data)
            except Exception as e:
                print(f"Error updating {args.player_name}: {e}")


if __name__ == "__main__":
    main()
