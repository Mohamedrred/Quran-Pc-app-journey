import requests
import time
import threading
import json
import os
import pygame
from ui_stuff import create_button_with_id_for_imgs
import importlib


api_base_url = "http://api.alquran.cloud/v1/"
images_api_base_url = "https://everyayah.com/data/images_png"

audio_stop = False
audio_paused = False

status = None

def file_exists(file_path):
    """Check if the file exists at the specified path."""
    return os.path.exists(file_path)

def download_online(url=None, file_path=None):
    """Download the audio file from the specified URL if it does not already exist at file_path."""
    if not file_exists(file_path):
        try:
            print(f"Downloading file from {url} to {file_path}...")
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for HTTP errors
            with open(file_path, "wb") as file:
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"Downloaded file successfully to {file_path}.")
        except requests.RequestException as e:
            print(f"Failed to download the file: {e}")
            return False
    else:
        print(f"File already exists at {file_path}.")
    return True

def play_audio(file_path):
    global audio_stop
    audio_stop = False

    """Play the audio file using Pygame."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()  # Initialize the mixer if not already done
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    try:
        pygame.mixer.music.load(file_path)
        # Loop the audio if loop_mode is True
        pygame.mixer.music.play()
        print("Playback started.")
    except pygame.error as e:
        print(f"Failed to load or play the audio file: {e}")

def pause_audio():
    global audio_paused
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        audio_paused = True
        print("Audio paused.")
    else:
        pygame.mixer.music.unpause()
        audio_paused = False
        print("Audio resumed.")

def stop_audio():
    global audio_stop
    if not pygame.mixer.get_init():
        pygame.mixer.init()  # Initialize the mixer if not already done
    pygame.mixer.music.stop()
    audio_stop = True

def check_json_file(file_name):
    if not os.path.exists(f"{file_name}.json"):
        # If the file doesn't exist, create it with an empty dictionary
        with open(f"{file_name}.json", "w") as file:
            json.dump({}, file)

def fetch_json_data(file_name='temp', api_endpoint='', create_json_file=True):
    check_json_file(file_name)
    data = None

    try:
        with open(f"{file_name}.json", 'r', encoding="utf-8") as data_json_tset:
            data = json.load(data_json_tset)
            if 'data' not in data:
                raise ValueError("Missing data")
    except (Exception, ValueError):
        req = requests.get(f'{api_base_url}{api_endpoint}')
        data = req.json()
        with open(f"{file_name}.json", 'w', encoding="utf-8") as data_json:
            json.dump(data, data_json, ensure_ascii=False, indent=4)

    # After processing, check if the file needs to be deleted
    if not create_json_file:
        path = os.path.abspath(f'{file_name}.json')
        os.remove(path)

    # Return the data regardless of whether the file is deleted or not
    return data['data']

def get_surah_names_list():
    surah_list = []

    check_json_file('surah_list')

    data = fetch_json_data('surah_list', 'surah')

    surah_list = [surah['name'] for surah in data]

    return surah_list

def get_reciters_names():
    reciters_list = []

    check_json_file('reciters_list')

    data = fetch_json_data('reciters_list', 'edition?format=audio&language=ar&type=versebyverse')

    reciters_list = [reciter['name'] for reciter in data]

    return reciters_list

def get_surah_and_reciter_info(surah_list, recitors_list):
    selected_reciter_name = recitors_list.get()
    selected_reciter_identifier = ''
    try:
        data = fetch_json_data('reciters_list', 'edition?format=audio&language=ar&type=versebyverse')
        for recitor_data in data:
            reciter_name = recitor_data['name']
            if selected_reciter_name == reciter_name:
                selected_reciter_identifier = recitor_data['identifier']
                break
    except Exception as e:
        print(f"Couldn't get surah reciter identifier : {e}")


    selected_surah_name = surah_list.get()
    selected_surah_number = surah_list._values.index(selected_surah_name) + 1

    surah_verses_number = 0
    with open("surah_list.json", 'r', encoding="utf-8") as surah_list_json_test:
        try:
            data = fetch_json_data('surah_list', 'surah')
            for surah_data in data:
                surah_name = surah_data['name']
                if selected_surah_name == surah_name:
                    surah_verses_number = surah_data['numberOfAyahs']
                    break

        except Exception as e:
            print(f"Couldn't get surah reciter identifier : {e}")

    audio_never_download = []
    audio_folder_path = f'Quran_audio/{selected_reciter_name}/{selected_surah_name}'

    images_never_download = []
    images_folder_path = f'Quran_images/{selected_surah_name}'

    for i in range(surah_verses_number):
        if file_exists(f'{audio_folder_path}/{i + 1}.mp3'):
            audio_never_download.append(i + 1)
        if file_exists(f'{images_folder_path}/{i + 1}.png'):
            images_never_download.append(i + 1)


    return surah_verses_number, images_never_download, audio_never_download, selected_surah_number, selected_surah_name, selected_reciter_name, selected_reciter_identifier, audio_folder_path, images_folder_path

def get_surah_or_verse_recition(surah_list, recitors_list, verse=None, for_verses=False):

    def threaded_download(main_link, secondary_link, file_path, selected_surah_name):
        if not download_online(main_link, file_path):
            print("Failed to download from Main link")
            if not download_online(secondary_link, file_path):
                print("Failed to download from secondary link")
            else:
                print(f"Download {selected_surah_name} in {file_path}")
        else:
            print(f"Download {selected_surah_name} in {file_path}")

    if for_verses:
        secondary_link = ''
        surah_verses_number, _, audio_never_download, selected_surah_number, selected_surah_name, selected_reciter_name, selected_reciter_identifier, audio_folder_path, _ = get_surah_and_reciter_info(
            surah_list, recitors_list)
        if not file_exists(f'{audio_folder_path}/{verse.id}'):
            data = fetch_json_data(api_endpoint=f'ayah/{selected_surah_number}:{verse.id}/{selected_reciter_identifier}',
                                   create_json_file=False)
            main_link = data['audio']
            try:
                secondary_link = data['audioSecondary'][0]
            except Exception:
                pass
            audio_folder_path = f'Quran_audio/{selected_reciter_name}/{selected_surah_name}'
            if not file_exists(audio_folder_path):
                os.makedirs(audio_folder_path)
            file_path = f'Quran_audio/{selected_reciter_name}/{selected_surah_name}/{verse.id}.mp3'

            # Start the download in a new thread
            thread = threading.Thread(target=threaded_download,
                                      args=(main_link, secondary_link, file_path, selected_surah_name))
            thread.start()
    else:
        secondary_link = ''
        surah_verses_number, _, audio_never_download, selected_surah_number, selected_surah_name, selected_reciter_name, selected_reciter_identifier, audio_folder_path, _ = get_surah_and_reciter_info(surah_list, recitors_list)
        if surah_verses_number != ((len(audio_never_download)) + 1):
            data = fetch_json_data(api_endpoint=f'surah/{selected_surah_number}/{selected_reciter_identifier}', create_json_file=False)
            ayahs = data['ayahs']
            for components in ayahs:
                main_link = components['audio']
                try:
                    secondary_link = components['audioSecondary'][0]
                except Exception:
                    pass
                ayah_number = components['numberInSurah']
                if ayah_number not in audio_never_download:
                    audio_folder_path = f'Quran_audio/{selected_reciter_name}/{selected_surah_name}'
                    if not file_exists(audio_folder_path):
                        os.makedirs(audio_folder_path)
                    file_path = f'Quran_audio/{selected_reciter_name}/{selected_surah_name}/{ayah_number}.mp3'

                    threaded_download(main_link, secondary_link, file_path, selected_surah_name)

def play_surah(surah_list, recitors_list):
    global audio_stop, audio_paused
    audio_stop = False
    audio_stop = False
    get_surah_or_verse_recition(surah_list, recitors_list)
    surah_verses_number, *_ ,audio_folder_path, _ = get_surah_and_reciter_info(surah_list, recitors_list)
    def main():
        i = 0
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        while i < surah_verses_number and not audio_stop:
            time.sleep(0.02)

            while audio_paused:
                time.sleep(0.05)
            i += 1
            if pygame.mixer.music.get_busy() and not audio_stop:
                i -= 1
            if not pygame.mixer.music.get_busy() and not audio_stop:
                play_audio(f'{audio_folder_path}/{i}.mp3')
    threading.Thread(target=main).start()
    
def get_verses_images(surah_list, recitors_list):
    surah_verses_number, images_never_download, _,  selected_surah_number, *_, images_folder_path = get_surah_and_reciter_info(surah_list, recitors_list)

    if surah_verses_number != ((len(images_never_download)) + 1):
        for i in range(surah_verses_number):
            if i not in images_never_download:
                os.makedirs(images_folder_path, exist_ok=True)
                download_online(f'{images_api_base_url}/{selected_surah_number}_{i + 1}.png', f'{images_folder_path}/{i + 1}.png')
            time.sleep(0.01)
    return surah_verses_number, images_folder_path

def play_vers(verse, surah_list, recitors_list):
    global audio_stop, audio_paused
    audio_stop = False
    audio_paused = False
    surah_verses_number, *_, audio_folder_path, _ = get_surah_and_reciter_info(surah_list, recitors_list)
    get_surah_or_verse_recition(surah_list, recitors_list, verse, for_verses=True)
    def main():
        i = verse.id
        while i < surah_verses_number + 1:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if audio_stop:
                break
            while audio_paused:
                time.sleep(0.02)
            if pygame.mixer.music.get_busy() and not audio_stop:
                time.sleep(0.02)
                continue

            verse_audio_path = f'{audio_folder_path}/{i}.mp3'
            play_audio(verse_audio_path)
            i += 1
            time.sleep(0.02)

    threading.Thread(target=main).start()

def show_verses(frame, surah_list, recitors_list):
    surah_verses_number, images_folder_path = get_verses_images(surah_list, recitors_list)
    def main():
        for widget in frame.winfo_children():
            widget.destroy()
            time.sleep(0.01)

        for i in range(surah_verses_number):
            button = create_button_with_id_for_imgs(frame, f'{images_folder_path}/{i + 1}.png', id=(i + 1))
            button.configure(command=lambda b=button: play_vers(b, surah_list, recitors_list))
            button.grid(row=i, column=0, sticky="ew")
            time.sleep(0.01)

    threading.Thread(target=main).start()

def set_volume(value):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.set_volume(float(value))

