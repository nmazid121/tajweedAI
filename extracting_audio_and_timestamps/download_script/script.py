import json
import requests
import os

# --- Configuration ---
# **IMPORTANT: Replace with the actual path to your JSON file**
QURAN_JSON_PATH = r'C:\Users\noobd\Desktop\TAJWEED AI\qul_downloads\audio\ayah-recitation-saud-al-shuraim-murattal-hafs-960.json\ayah-recitation-saud-al-shuraim-murattal-hafs-960.json'
OUTPUT_ROOT_DIR = "downloaded_quran_audio_direct_shuraim"

# List of Surah numbers for the surahs you want to download.
# We'll use this to filter the huge JSON.
SURAH_NUMBERS_TO_DOWNLOAD = [
    1,   # Al-Fatiha
    111, # Al-Lahab
    112, # Al-Ikhlas
    113, # Al-Falaq
    109, # Al-Kafirun
    82   # Al-Infitar
]

# A simple mapping for user-friendly directory names
# You might want a more comprehensive mapping if you download many surahs
SURAH_NUMBER_TO_NAME = {
    1: "Al-Fatiha",
    111: "Al-Lahab",
    112: "Al-Ikhlas",
    113: "Al-Falaq",
    109: "Al-Kafirun",
    82: "Al-Infitar"
}

# --- Helper Function for Padding Numbers (still useful for file naming if preferred) ---
def pad_number(num, length=3):
    """Pads a number with leading zeros to a specified length."""
    return str(num).zfill(length)

# --- Main Download Logic ---
def download_ayahs_from_json():
    # Create the root output directory if it doesn't exist
    os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

    try:
        # Load the huge JSON file
        with open(QURAN_JSON_PATH, 'r', encoding='utf-8') as f:
            quran_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at '{QURAN_JSON_PATH}'. Please check the path.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{QURAN_JSON_PATH}'. Check if it's valid JSON.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while loading JSON: {e}")
        return

    download_count = 0
    skipped_count = 0
    ayahs_to_process = []

    # First pass: Filter and collect relevant ayah data
    print("Filtering JSON for specified surahs...")
    for key, ayah_info in quran_data.items():
        if isinstance(ayah_info, dict): # Ensure it's a dictionary entry
            surah_number = ayah_info.get("surah_number")
            if surah_number in SURAH_NUMBERS_TO_DOWNLOAD:
                ayahs_to_process.append(ayah_info)
    
    # Sort ayahs for organized downloading (optional but good practice)
    ayahs_to_process.sort(key=lambda x: (x.get("surah_number", 0), x.get("ayah_number", 0)))

    print(f"Found {len(ayahs_to_process)} ayahs to potentially download from specified surahs.")

    current_surah_dir = None
    last_surah_number = None

    for ayah_info in ayahs_to_process:
        surah_number = ayah_info.get("surah_number")
        ayah_number = ayah_info.get("ayah_number")
        audio_url = ayah_info.get("audio_url")

        if surah_number is None or ayah_number is None or audio_url is None:
            print(f"Warning: Skipping malformed ayah entry: {ayah_info}")
            continue

        if surah_number != last_surah_number:
            surah_name = SURAH_NUMBER_TO_NAME.get(surah_number, f"Surah_{pad_number(surah_number)}")
            current_surah_dir = os.path.join(OUTPUT_ROOT_DIR, f"{pad_number(surah_number)}_{surah_name}")
            os.makedirs(current_surah_dir, exist_ok=True)
            print(f"\n--- Processing Surah {surah_number}: {surah_name} ---")
            last_surah_number = surah_number

        # Extract filename from URL or create a standardized one
        # Using a standardized name for consistency: Ayah_001.mp3
        local_filename = f"Ayah_{pad_number(ayah_number)}.mp3"
        local_filepath = os.path.join(current_surah_dir, local_filename)

        if os.path.exists(local_filepath):
            print(f"Skipping: {local_filename} already exists in {os.path.basename(current_surah_dir)}")
            skipped_count += 1
            continue

        try:
            print(f"Downloading {surah_name} Ayah {ayah_number} from {audio_url}...")
            response = requests.get(audio_url, stream=True, timeout=30) # Increased timeout
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

            with open(local_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {local_filename}")
            download_count += 1
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {audio_url}: {e}")
            print(f"Could not download Ayah {ayah_number} from Surah {surah_name}.")
        except Exception as e:
            print(f"An unexpected error occurred for Ayah {ayah_number} from Surah {surah_name}: {e}")

    print(f"\n--- Download Summary ---")
    print(f"Total downloaded files: {download_count}")
    print(f"Total skipped (already exists): {skipped_count}")
    print(f"Process complete.")

# --- Run the downloader ---
if __name__ == "__main__":
    download_ayahs_from_json()