from ui_stuff import *
from api_stuff import *

def main():
    app = ctk.CTk()
    app.title('quran')
    app.geometry("1280x717")

    right_frame = ctk.CTkScrollableFrame(app, width=300, height=200)
    right_frame.grid(row=0, column=1)
    right_frame.grid_columnconfigure(0, weight=1)

    ########################################################

    left_frame = ctk.CTkScrollableFrame(app, width=300, height=200)
    for i in range(4):
        left_frame.columnconfigure(i, weight=1)
        left_frame.rowconfigure(i, weight=1, minsize=38)
    left_frame.grid(row=0, column=0)

    surah_list_option_menu = create_optionmenu(left_frame, values=get_surah_names_list(), anchor='e', command=lambda _: show_verses(right_frame, surah_list_option_menu, recitors_list_option_menu))
    surah_list_option_menu.grid(row=0, column=0)
    recitors_list_option_menu = create_optionmenu(left_frame, values=get_reciters_names(), anchor='e')
    recitors_list_option_menu.grid(row=0, column=1)

    # Play surah button
    start_surah_btn = create_button(left_frame, anchor='center', text='بدأ السورة',
                                    command=lambda: play_surah(surah_list_option_menu, recitors_list_option_menu))
    start_surah_btn.grid(row=1, column=0)

    # Pause audio button
    pause_audio_btn = create_button(left_frame, anchor='center', text='توقف',
                                    command=lambda: pause_audio())
    pause_audio_btn.grid(row=1, column=1)

    # Stop audio button
    stop_audio_btn = create_button(left_frame, anchor='center', text='ايقاف',
                                   command=lambda: stop_audio())
    stop_audio_btn.grid(row=2, column=0, columnspan=2)

    # Audio volume control slider
    audio_control = create_slider(left_frame, command=lambda _: set_volume(audio_control.get()))
    audio_control.grid(row=4, column=0)
    def on_resize(event):
        left_frame.configure(height=app.winfo_height())
        right_frame.configure(height=app.winfo_height())
        right_frame.configure(width=(app.winfo_width() - left_frame.cget('width') - 45))

    app.bind("<Configure>", on_resize)
    app.mainloop()



if __name__ == "__main__":
    main()