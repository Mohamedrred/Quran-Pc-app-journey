import pygame
import tkinter as tk
from tkinter import ttk
import threading
import time
import requests
import os
from PIL import Image, ImageTk


quran_font = "Quran karim 114.tff"
base_url = "https://api.quran.com/api/v4/"
verses_base_url = 'https://verses.quran.com/'
surahs_names = []
reciters_names = []

# Dictionary to store dynamic variables
dynamic_variables = {}

loop_mode_checkbutton_var = None
continue_from_verse_checkbutton_var = None
never_stop_var = None
stop_verses = False
is_paused = False


def file_exists(file_path):
    """Check if the file exists at the specified path."""
    return os.path.exists(file_path)


def download_audio(url, file_path):
    """Download the audio file from the specified URL if it does not already exist at file_path."""
    if not file_exists(file_path):
        try:
            print(f"Downloading audio from {url} to {file_path}...")
            req = requests.get(url, stream=True)
            req.raise_for_status()  # Raise an exception for HTTP errors
            with open(file_path, "wb") as file:
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"Downloaded audio successfully to {file_path}.")
        except requests.RequestException as e:
            print(f"Failed to download the file: {e}")
            return False
    else:
        print(f"File already exists at {file_path}.")
    return True


def download_all_verses():
    """Play the audio for a specific verse, handling pagination if necessary."""
    surah_name = dynamic_variables['Surah Names']['value']
    reciter_name = dynamic_variables['Reciters Names']['value']
    surah_id = dynamic_variables['Surah Names']['index'] + 1
    reciter_id = dynamic_variables['Reciters Names']['index'] + 1
    d = 0

    def fetch_and_play():
        all_audio_files = fetch_all_audio_files(base_url, reciter_id, surah_id)
        x = 0
        for i in all_audio_files:
            if d < 150:
                verse_info = all_audio_files[x]
                url = f'https:{verse_info["url"]}' if reciter_id in [6, 11,
                                                                     12] else f'{verses_base_url}{verse_info["url"]}'
                os.makedirs(f'quran\\{reciter_name}\\{surah_name}',
                            exist_ok=True)
                file_path = f'quran\\{reciter_name}\\{surah_name}\\{verse_info["verse_key"]}.mp3'
                threading.Thread(target=download_audio, args=(url, file_path)).start()
                x += 1
            else:
                time.sleep(10)

    threading.Thread(target=fetch_and_play).start()


def play_audio(file_path):
    stop_verses = False
    """Play the audio file using Pygame."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()  # Initialize the mixer if not already done
    try:
        pygame.mixer.music.load(file_path)
        # Loop the audio if loop_mode is True
        pygame.mixer.music.play(loops=-1 if loop_mode_checkbutton_var.get() else 0)
        print("Playback started.")
    except pygame.error as e:
        print(f"Failed to load or play the audio file: {e}")


def pause_audio():
    global is_paused
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        is_paused = True
        print("Audio paused.")
    else:
        pygame.mixer.music.unpause()
        is_paused = False
        print("Audio resumed.")


def stop_audio():
    global stop_verses
    if not pygame.mixer.get_init():
        pygame.mixer.init()  # Initialize the mixer if not already done
    """Stop any audio file currently playing."""
    stop_verses = True
    pygame.mixer.music.stop()
    print("Audio stopped.")


def play_surah():
    global stop_verses
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    """Start audio download and playback."""
    if 'Surah Names' in dynamic_variables and 'Reciters Names' in dynamic_variables:
        surah_name = dynamic_variables['Surah Names']['value']
        reciter_name = dynamic_variables['Reciters Names']['value']
        surah_id = dynamic_variables['Surah Names']['index'] + 1
        reciter_id = dynamic_variables['Reciters Names']['index'] + 1
        def never_stop(surah_id):
            while never_stop_var.get() and not stop_verses:
                print(stop_verses)
                if surah_id < 115:
                    req = requests.get(f'https://api.quran.com/api/v4/chapter_recitations/{reciter_id}/{surah_id}')
                    data = req.json()
                    url = data['audio_file']['audio_url']
                    os.makedirs(f'quran\\{reciter_name}', exist_ok=True)
                    file_path = f'quran\\{reciter_name}\\{surah_id}.mp3'
                    if pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(90)
                        continue
                    if download_audio(url, file_path):
                        threading.Thread(target=play_audio(file_path)).start()
                    else:
                        print("Failed to download or play audio.")
                    surah_id += 1
                else:
                    surah_id = 0
        try:
            if never_stop_var.get():
                threading.Thread(target=never_stop, args=(surah_id,)).start()
            else:
                req = requests.get(f'https://api.quran.com/api/v4/chapter_recitations/{reciter_id}/{surah_id}')
                data = req.json()
                url = data['audio_file']['audio_url']
                os.makedirs(f'quran\\{reciter_name}', exist_ok=True)
                file_path = f'quran\\{reciter_name}\\{surah_id}.mp3'
                if download_audio(url, file_path):
                    play_audio(file_path)
                else:
                    print("Failed to download or play audio.")
        except requests.RequestException as e:
            print(f"Failed to fetch audio URL: {e}")
    else:
        print("Dynamic variables for 'Surah Names' or 'Reciters Names' are not set.")


def play_verse(verse_id):
    global stop_verses, is_paused
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    """Play the audio for a specific verse, handling pagination if necessary."""
    surah_name = dynamic_variables['Surah Names']['value']
    reciter_name = dynamic_variables['Reciters Names']['value']
    surah_id = dynamic_variables['Surah Names']['index'] + 1
    reciter_id = dynamic_variables['Reciters Names']['index'] + 1
    stop_verses = False

    def fetch_and_play():
        all_audio_files = fetch_all_audio_files(base_url, reciter_id, surah_id)
        if verse_id < len(all_audio_files):
            if continue_from_verse_checkbutton_var.get():
                x = 0
                for i in all_audio_files:
                    if stop_verses:
                        break
                    verse_info = all_audio_files[int(verse_id + x)]
                    url = f'https:{verse_info["url"]}' if reciter_id in [6, 11,
                                                                         12] else f'{verses_base_url}{verse_info["url"]}'

                    os.makedirs(f'quran\\{reciter_name}\\{surah_name}',
                                exist_ok=True)
                    file_path = f'quran\\{reciter_name}\\{surah_name}\\{verse_info["verse_key"]}.mp3'
                    if download_audio(url, file_path):
                        # Handle pause before playing the next verse
                        while is_paused:
                            time.sleep(0.05)  # Wait if paused

                        play_audio(file_path)
                        while pygame.mixer.music.get_busy() or is_paused:
                            time.sleep(0.05)
                    else:
                        print("Failed to download or play audio.")
                    x += 1
            else:
                verse_info = all_audio_files[int(verse_id)]
                url = f'https:{verse_info["url"]}' if reciter_id in [6, 11,
                                                                     12] else f'{verses_base_url}{verse_info["url"]}'

                os.makedirs(f'quran\\{reciter_name}\\{surah_name}', exist_ok=True)
                file_path = f'quran\\{reciter_name}\\{surah_name}\\{verse_info["verse_key"]}.mp3'
                if download_audio(url, file_path):
                    play_audio(file_path)
                else:
                    print("Failed to download or play audio.")
        else:
            print(f"Verse ID {verse_id} not found in audio files.")

    # Run the fetch and play process in a separate thread
    threading.Thread(target=fetch_and_play).start()


def fetch_all_audio_files(base_url, reciter_id, surah_id):
    """Fetch all audio files for a given reciter and surah, handling pagination using threading."""

    def fetch_page(page, results):
        """Fetch a single page of audio files."""
        url = f'{base_url}recitations/{reciter_id}/by_chapter/{surah_id}?page={page}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            results[page] = data.get('audio_files', [])
        except requests.RequestException as e:
            print(f"Failed to fetch data from page {page}: {e}")

    all_audio_files = []
    current_page = 1
    total_pages = 1
    threads = []
    results = {}

    # Initial request to determine total pages
    initial_url = f'{base_url}recitations/{reciter_id}/by_chapter/{surah_id}?page={current_page}'
    try:
        response = requests.get(initial_url)
        response.raise_for_status()
        data = response.json()
        pagination = data.get('pagination', {})
        total_pages = pagination.get('total_pages', 1)
    except requests.RequestException as e:
        print(f"Failed to fetch initial data: {e}")
        return []

    # Fetch all pages concurrently
    for page in range(1, total_pages + 1):
        thread = threading.Thread(target=fetch_page, args=(page, results))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Combine results from all pages
    for page in range(1, total_pages + 1):
        all_audio_files.extend(results.get(page, []))

    return all_audio_files


def set_volume(val):
    try:
        volume = int(val) / 100
        pygame.mixer.music.set_volume(volume)
    except Exception:
        pass


def get_surahs_names():
    req = requests.get(f'{base_url}chapters')
    data = req.json()
    try:
        for chapter in data['chapters']:
            surahs_names.append(chapter['name_arabic'])
    except Exception as e:
        print("Error fetching surah names:", e)


def get_reciters_name():
    req = requests.get(f'{base_url}resources/recitations')
    data = req.json()
    try:
        for recitation in data['recitations']:
            reciters_names.append(recitation['reciter_name'])
    except Exception as e:
        print("Error fetching reciter names:", e)


def get_verse_image_path(directory, surah_number):
    # Get a list of all subdirectories in the main directory
    folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
    folders.sort()

    # Access the folder corresponding to the given surah_number
    surah_folder = folders[surah_number]
    surah_folder_get = os.path.join(directory, surah_folder)
    surah_folder_path = os.path.abspath(surah_folder_get)

    return surah_folder_path


def update_dynamic_variable(name, index, value):
    """Update dynamic variable based on combobox selection."""
    dynamic_variables[name] = {'index': index, 'value': value}


def on_combobox_select(event):
    """Handle combobox selection."""
    selected_combobox = event.widget
    selected_index = selected_combobox.current()
    selected_value = selected_combobox.get()

    if selected_combobox == surahs_names_list:
        update_dynamic_variable("Surah Names", selected_index, selected_value)
    elif selected_combobox == reciters_name:
        update_dynamic_variable("Reciters Names", selected_index, selected_value)


def create_combobox_with_label(master, row, column, values, label_text, bg='#ffffff', fg='#000000'):
    frame = tk.Frame(master, bg=bg)
    frame.grid(row=row, column=column, sticky='ew', padx=10, pady=10)
    frame.columnconfigure(0, weight=1)  # Ensure the frame expands

    label = tk.Label(frame, text=label_text, bg=bg, fg=fg, font=(quran_font, 12, 'bold'))
    label.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))

    combobox = ttk.Combobox(frame, values=values, font=(quran_font, 12))
    combobox.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
    combobox.bind("<<ComboboxSelected>>", on_combobox_select)  # Bind the select event

    return combobox


def create_button(master, row, column, text, command, bg='#ffffff', fg='#000000'):
    button = tk.Button(master, text=text, bg=bg, fg=fg, font=(quran_font, 12, 'bold'),
                       command=command, relief='raised', borderwidth=2)
    button.grid(row=row, column=column, sticky='ew', padx=10, pady=5)
    return button


def create_button_with_id_for_verses(master, row, column, image, command, id=None):
    img = Image.open(image)

    # Convert the image to a format Tkinter can use
    tk_img = ImageTk.PhotoImage(img)

    # Create the button
    button = tk.Button(master, image=tk_img, command=command)

    # Keep a reference to the image to prevent garbage collection
    button.image = tk_img

    button.grid(row=row, column=column, padx=10, pady=5, sticky='ew')
    button.id = id
    return button


def main():
    global surahs_names_list, reciters_name, loop_mode_checkbutton_var, continue_from_verse_checkbutton_var, never_stop_var

    # Initialize the main window
    root = tk.Tk()
    root.title("القران")
    root.geometry("1280x717")
    root.configure(bg='#2C2C2C')  # Dark teal background
    root.resizable(True, True)  # Allow resizing
    root.columnconfigure(0, weight=1)

    never_stop_var = tk.BooleanVar()
    # Create BooleanVar for loop mode Checkbutton
    loop_mode_checkbutton_var = tk.BooleanVar()
    # Create BooleanVar for continue_from_verse Checkbutton
    continue_from_verse_checkbutton_var = tk.BooleanVar()

    # Fetch data for comboboxes
    get_surahs_names()
    get_reciters_name()

    # Create and place frames for organization with Quranic theme colors
    top_frame = tk.Frame(root, bg='#2C2C2C')  # Dark green
    top_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=10)
    top_frame.columnconfigure(0, weight=1)
    top_frame.columnconfigure(1, weight=1)

    # Create and place comboboxes in the top frame with gold and white styling
    surahs_names_list = create_combobox_with_label(
        top_frame, 0, 0, surahs_names, "Surah Names", bg='#2C2C2C', fg='#E0E0E0')
    reciters_name = create_combobox_with_label(
        top_frame, 0, 1, reciters_names, "Reciters Names", bg='#2C2C2C', fg='#E0E0E0')

    # Canvas for scrollable area
    canvas = tk.Canvas(root, bg='#2C2C2C')
    canvas.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 10))

    # Scrollbars
    vertical_scrollbar = tk.Scrollbar(root, orient='vertical', command=canvas.yview)
    vertical_scrollbar.grid(row=1, column=1, sticky='ns')
    canvas.configure(yscrollcommand=vertical_scrollbar.set)

    # Create a frame inside the canvas to hold buttons
    middle_frame = tk.Frame(canvas, bg='#2C2C2C')
    middle_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Center horizontally within middle_frame
    middle_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its content
    middle_frame.pack(fill=tk.BOTH, expand=True)  # Allow the frame to expand

    canvas.create_window((0, 0), window=middle_frame, anchor='nw')  # Anchor 'nw' aligns the frame to the top-left

    # Fetch and display verses as buttons
    def get_surah_text():
        if 'Surah Names' in dynamic_variables:
            surah_id = dynamic_variables['Surah Names']['index'] + 1
            try:
                req = requests.get(f'{base_url}quran/verses/uthmani?chapter_number={surah_id}')
                req.raise_for_status()
                data = req.json()

                verses = data.get('verses', [])
                if not verses:
                    print("No verses found for this surah.")
                    return

                for widget in middle_frame.winfo_children():
                    widget.destroy()

                for index, verse in enumerate(verses):
                    verse_id = index + 1  # Unique ID for each button
                    verse_img_path = get_verse_image_path('quranpngs', surah_id)
                    get_verse_img_path = os.path.join(verse_img_path, f'{surah_id}_{verse_id}.png')
                    create_button_with_id_for_verses(middle_frame, index, 0, get_verse_img_path,
                                                     lambda vid=verse_id - 1: play_verse(vid),
                                                     id=verse_id)
                    time.sleep(0.005)

                # Update scroll region and center the frame horizontally
                update_scroll_region()

            except requests.RequestException as e:
                print(f"Error fetching surah text: {e}")
            except KeyError as e:
                print(f"Key error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    # Update the scroll region and center the frame horizontally
    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox('all'))

    bottom_frame = tk.Frame(root, bg='#2C2C2C')  # Dark teal
    bottom_frame.grid(row=2, column=0, sticky='ew', padx=15, pady=15)
    bottom_frame.columnconfigure(0, weight=1)
    bottom_frame.columnconfigure(1, weight=1)
    bottom_frame.columnconfigure(2, weight=1)

    # Place the start button in the bottom frame
    create_button(bottom_frame, 0, 1, "عرض السورة", get_surah_text, bg='#009688', fg='white')  # start button
    create_button(bottom_frame, 0, 2, "تحميل كل الايات", download_all_verses, bg='#009688', fg='white')

    # Add bottom section buttons for controlling audio with modern design
    create_button(bottom_frame, 1, 0, "تشغيل", play_surah, bg='#009688', fg='white')  # start button
    create_button(bottom_frame, 1, 1, "توقف", pause_audio, bg='#e6c400', fg='white')  # pause button
    create_button(bottom_frame, 1, 2, "ايقاف", stop_audio, bg='#e64a19', fg='white')  # stop button

    # Create a Checkbutton for loop mode in the bottom frame
    loop_checkbutton = tk.Checkbutton(bottom_frame, text="تكرار", variable=loop_mode_checkbutton_var,
                                      font=(quran_font, 12, 'bold'))
    loop_checkbutton.grid(row=2, column=0, sticky='ew', padx=10, pady=5)

    # Create a Checkbutton for continue to next surah in the bottom frame
    never_stop = tk.Checkbutton(bottom_frame, text="عدم التوقف ابدا", variable=never_stop_var,
                                      font=(quran_font, 12, 'bold'))
    never_stop.grid(row=3, column=0, sticky='ew', padx=10, pady=5)

    # Create a Checkbutton for continue verse mode in the bottom frame
    continue_from_verse_checkbutton = tk.Checkbutton(bottom_frame, text="تابع من الاية",
                                                     variable=continue_from_verse_checkbutton_var,
                                                     font=(quran_font, 12, 'bold'))
    continue_from_verse_checkbutton.grid(row=2, column=1, sticky='ew', padx=10, pady=5)

    # Create a scale widget for volume control
    volume_scale = tk.Scale(bottom_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=set_volume)
    volume_scale.set(10)  # Set the initial volume to 50%
    volume_scale.grid(row=3, column=1)

    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
