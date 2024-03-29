import os
import json
import requests
from bs4 import BeautifulSoup

def get_game_name_and_icon_name(full_icon_name):
    # Example full_icon_name: Castle-of-Shikigami-2-icon001-%5B010061E018D3C000%5D.jpg
    parts = full_icon_name.split('-')
    
    # Extract game name and icon name
    game_name_parts = parts[:-3]
    icon_name = '-'.join(parts[-3:-1])

    # Special case for names with multiple hyphens, join everything before the last hyphen
    if len(game_name_parts) > 1:
        game_name = ' '.join(game_name_parts[:-1])
    elif len(game_name_parts) == 1:
        game_name = game_name_parts[0]
    else:
        # Handle the case where game_name_parts is an empty list
        game_name = "NULL"

    return game_name, icon_name

def get_title_id(full_icon_name):
    # Extract title ID from the filename
    start_indicator = '%5B'
    end_indicator = '%5D'
    
    start_idx = full_icon_name.find(start_indicator, 0)
    end_idx = full_icon_name.find(end_indicator, start_idx)

    # Check if both indicators are found and have a valid range
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        title_id = full_icon_name[start_idx + len(start_indicator):end_idx]
        return title_id
    else:
        # Return None or raise an exception based on your preference for handling invalid cases
        return None


def fetch_icons(base_url, subdirectories):
    icons_data = []

    for subdirectory in subdirectories:
        subdirectory_url = os.path.join(base_url, subdirectory)

        # Fetch the list of files in the subdirectory using GitHub API
        api_url = f'https://api.github.com/repos/sodasoba1/NSW-Custom-Game-Icons-square/contents/Default/{subdirectory}?ref=main'
        response = requests.get(api_url)
        files_info = response.json()

        # Filter only .jpg and .png files
        image_files = [file_info['download_url'] for file_info in files_info if file_info['name'].lower().endswith(('.jpg', '.png'))]

        # Extract game name and icon name for each image
        for image_link in image_files:
            game_name, icon_name = get_game_name_and_icon_name(os.path.basename(image_link))
            title_id = get_title_id(os.path.basename(image_link))
            
            author = "sodasoba"
            icon_data = {"name": icon_name, "url": image_link, "author": author}

            # Check if the game entry already exists in icons_data based on title ID
            existing_entry = next((entry for entry in icons_data if entry.get("title_id") == title_id), None)

            if existing_entry:
                existing_entry["normalIcon"] = image_link
                existing_entry["icons"].append(icon_data)
            else:
                game_entry = {"title_id": title_id, "name": game_name, "normalIcon": image_link, "icons": [icon_data]}
                icons_data.append(game_entry)

    return icons_data




def merge_with_existing_json(existing_json_path, new_icons_data):
    # If the existing JSON file doesn't exist, create an empty data structure
    if not os.path.exists(existing_json_path):
        existing_data = {"games": []}
    else:
        with open(existing_json_path, 'r') as existing_json_file:
            existing_data = json.load(existing_json_file)

    # Update or add games from new_icons_data to existing_data
    for new_game_entry in new_icons_data:
        existing_game_entry = next((entry for entry in existing_data["games"] if entry["name"] == new_game_entry["name"]), None)
        
        if existing_game_entry:
            # Update existing game entry
            existing_game_entry["normalIcon"] = new_game_entry["normalIcon"]
            existing_game_entry["icons"].extend(new_game_entry["icons"])
        else:
            # Add new game entry
            existing_data["games"].append(new_game_entry)

    return existing_data

def main():
    base_url = "https://raw.githubusercontent.com/sodasoba1/NSW-Custom-Game-Icons-square/main/Default/"
    subdirectories = ["0-9", "A", "Arcade-archive", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", 
                      "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    
    sodasoba_icons_data = fetch_icons(base_url, subdirectories)

    # Load existing icons.json data
    existing_json_path = "icons.json"
    with open(existing_json_path, 'r') as existing_json_file:
        existing_data = json.load(existing_json_file)

    # Merge sodasoba_icons_data with existing_data
    merged_data = merge_with_existing_json(existing_json_path, sodasoba_icons_data)

    # Create JSON file
    output_file_path = "output.json"
    with open(output_file_path, "w") as json_file:
        json.dump(merged_data, json_file, indent=2)

if __name__ == "__main__":
    main()
