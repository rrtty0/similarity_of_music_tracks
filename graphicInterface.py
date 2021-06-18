from tkinter import filedialog
from tkinter import *
import ctypes
import tkinter.ttk as ttk
import ProcessMusicTrack
from enum import Enum
import shutil
import threading
import os.path


class ShowImageMode(Enum):
    SPECTRUM = 'Spectrum'
    PROBABILITY = 'Probability'

def get_screen_size():
    user32 = ctypes.windll.user32
    screen_size = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    return screen_size

def check_run_button():
    if txt_first_track_name.get() != '' and txt_second_track_name.get() != '':
        btn_run.configure(state=NORMAL)
    else:
        btn_run.configure(state=DISABLED)

def first_track_button_clicked():
    global file_first_track
    cpy_file_name = file_first_track
    try:
        file_first_track = filedialog.askopenfilename(
            filetypes=(("Music files", "*.ogg"), ("Music files", "*.mp3"), ("Music files", "*.wav")))
        track_name = re.search(r'[^/]*\.((wav)|(ogg)|(mp3))$', str(file_first_track)).group(0)
        if str(cpy_file_name) != '':
            last_track_name = re.search(r'[^/]*\.((wav)|(ogg)|(mp3))$', str(cpy_file_name)).group(0)
            if os.path.exists('music/' + str(last_track_name)[0:len(str(last_track_name)) - 4]):
                shutil.rmtree(str(cpy_file_name)[0:len(str(cpy_file_name)) - 4])
        txt_first_track_name.configure(state=NORMAL)
        txt_first_track_name.delete(0, END)
        txt_first_track_name.insert(0, track_name)
        txt_first_track_name.configure(state=DISABLED)
        check_run_button()
        btn_show_details.configure(state=DISABLED)
        label_result.config(text="Result:")
        global created_folder_first_track
        created_folder_first_track = False
        print(txt_first_track_name.get())
    except AttributeError:
        print('not')
        file_first_track = cpy_file_name
        return

def second_track_button_clicked():
    global file_second_track
    cpy_file_name = file_second_track
    try:
        file_second_track = filedialog.askopenfilename(
            filetypes=(("Music files", "*.ogg"), ("Music files", "*.mp3"), ("Music files", "*.wav")))
        track_name = re.search(r'[^/]*\.((wav)|(ogg)|(mp3))$', str(file_second_track)).group(0)
        if str(cpy_file_name) != '':
            last_track_name = re.search(r'[^/]*\.((wav)|(ogg)|(mp3))$', str(cpy_file_name)).group(0)
            if os.path.exists('music/' + str(last_track_name)[0:len(str(last_track_name)) - 4]):
                shutil.rmtree(str(cpy_file_name)[0:len(str(cpy_file_name)) - 4])
        txt_second_track_name.configure(state=NORMAL)
        txt_second_track_name.delete(0, END)
        txt_second_track_name.insert(0, track_name)
        txt_second_track_name.configure(state=DISABLED)
        check_run_button()
        btn_show_details.configure(state=DISABLED)
        label_result.config(text="Result:")
        global created_folder_second_track
        created_folder_second_track = False
        print(txt_second_track_name.get())
    except:
        print('not')
        file_second_track = cpy_file_name
        return

def check_buttons(track, btn_prev, btn_next, index):
    if index == 0:
        btn_prev.configure(state=DISABLED)
    else:
        btn_prev.configure(state=NORMAL)
    if selected_title_tab1.get() == 0:
        if index == len(track.spectral_matrix) - 1:
            btn_next.configure(state=DISABLED)
        else:
            btn_next.configure(state=NORMAL)
    else:
        if index == len(track.distribution_density_for_notes) - 1:
            btn_next.configure(state=DISABLED)
        else:
            btn_next.configure(state=NORMAL)

def show_title_tab1():
    if selected_title_tab1.get() == 0:
        label_title_tab1.configure(text="Notes spectrum")
        check_buttons(processed_first_track, btn_previous_tab1, btn_next_tab1, index_of_images[0][0])
        index_spinbox_tab1.config(to_=len(processed_first_track.spectral_matrix) - 1)
        change_spinbox(index_spinbox_tab1, index_of_images[0][0])
        show_image(index_of_images[0][0], processed_first_track, label_image_tab1, index_spinbox_tab1, ShowImageMode.SPECTRUM.value)
    else:
        if selected_title_tab1.get() == 1:
            label_title_tab1.configure(text="Probability distribution")
            check_buttons(processed_first_track, btn_previous_tab1, btn_next_tab1, index_of_images[0][1])
            index_spinbox_tab1.configure(to_=len(processed_first_track.distribution_density_for_notes) - 1)
            change_spinbox(index_spinbox_tab1, index_of_images[0][1])
            show_image(index_of_images[0][1], processed_first_track, label_image_tab1, index_spinbox_tab1, ShowImageMode.PROBABILITY.value)

def show_title_tab2():
    if selected_title_tab2.get() == 0:
        label_title_tab2.configure(text="Notes spectrum")
        check_buttons(processed_second_track, btn_previous_tab2, btn_next_tab2, index_of_images[1][0])
        index_spinbox_tab2.config(to_=len(processed_second_track.spectral_matrix) - 1)
        change_spinbox(index_spinbox_tab2, index_of_images[1][0])
        show_image(index_of_images[1][0], processed_second_track, label_image_tab2, index_spinbox_tab2,
                   ShowImageMode.SPECTRUM.value)
    else:
        if selected_title_tab2.get() == 1:
            label_title_tab2.configure(text="Probability distribution")
            check_buttons(processed_second_track, btn_previous_tab2, btn_next_tab2, index_of_images[1][1])
            index_spinbox_tab2.config(to_=len(processed_second_track.distribution_density_for_notes) - 1)
            change_spinbox(index_spinbox_tab2, index_of_images[1][1])
            show_image(index_of_images[1][1], processed_second_track, label_image_tab2, index_spinbox_tab2,
                       ShowImageMode.PROBABILITY.value)

def read_image(index, track, show_image_mode):
    fille = ''
    if show_image_mode == ShowImageMode.SPECTRUM.value:
        fille = track.output_graphic_of_spectral_matrix(index)
    if show_image_mode == ShowImageMode.PROBABILITY.value:
        fille = track.output_graphic_of_probability_distribution(index)
    return fille

def change_spinbox(index_spinbox, value):
    index_spinbox.delete(0, END)
    index_spinbox.insert(0, value)

def show_image(index, track, label_image, index_spinbox, show_image_mode):
    photoImage = PhotoImage(file=read_image(index, track, show_image_mode))
    label_image.configure(image=photoImage)
    details_window.mainloop()

def btn_next_tab1_clicked():
    if selected_title_tab1.get() == 0:
        len_images = len(processed_first_track.spectral_matrix)
    else:
        len_images = len(processed_first_track.distribution_density_for_notes)
    show_next_image(processed_first_track, label_image_tab1, index_spinbox_tab1, btn_previous_tab1, btn_next_tab1,
                    selected_title_tab1, index_of_images[0], len_images)

def btn_prev_tab1_clicked():
    if selected_title_tab1.get() == 0:
        len_images = len(processed_first_track.spectral_matrix)
    else:
        len_images = len(processed_first_track.distribution_density_for_notes)
    show_previous_image(processed_first_track, label_image_tab1, index_spinbox_tab1, btn_previous_tab1, btn_next_tab1,
                        selected_title_tab1, index_of_images[0], len_images)

def changed_spinbox_tab1():
    if selected_title_tab1.get() == 0:
        len_images = len(processed_first_track.spectral_matrix)
    else:
        len_images = len(processed_first_track.distribution_density_for_notes)
    if int(index_spinbox_tab1.get()) >= len_images:
        change_spinbox(index_spinbox_tab1, len_images - 1)
    if int(index_spinbox_tab1.get()) < 0:
        change_spinbox(index_spinbox_tab1, 0)
    #print(index_spinbox_tab1.get())
    change_image(processed_first_track, label_image_tab1, index_spinbox_tab1, btn_previous_tab1, btn_next_tab1,
                 selected_title_tab1, index_of_images[0], len_images)

def btn_next_tab2_clicked():
    if selected_title_tab2.get() == 0:
        len_images = len(processed_second_track.spectral_matrix)
    else:
        len_images = len(processed_second_track.distribution_density_for_notes)
    show_next_image(processed_second_track, label_image_tab2, index_spinbox_tab2, btn_previous_tab2, btn_next_tab2,
                    selected_title_tab2, index_of_images[1], len_images)

def btn_prev_tab2_clicked():
    if selected_title_tab2.get() == 0:
        len_images = len(processed_second_track.spectral_matrix)
    else:
        len_images = len(processed_second_track.distribution_density_for_notes)
    show_previous_image(processed_second_track, label_image_tab2, index_spinbox_tab2, btn_previous_tab2, btn_next_tab2,
                        selected_title_tab2, index_of_images[1], len_images)

def changed_spinbox_tab2():
    if selected_title_tab2.get() == 0:
        len_images = len(processed_second_track.spectral_matrix)
    else:
        len_images = len(processed_second_track.distribution_density_for_notes)
    if int(index_spinbox_tab2.get()) >= len_images:
        change_spinbox(index_spinbox_tab2, len_images - 1)
    if int(index_spinbox_tab2.get()) < 0:
        change_spinbox(index_spinbox_tab2, 0)
    #print(index_spinbox_tab2.get())
    change_image(processed_second_track, label_image_tab2, index_spinbox_tab2, btn_previous_tab2, btn_next_tab2,
                 selected_title_tab2, index_of_images[1], len_images)

def show_next_image(track, label_image, index_spinbox, btn_prev, btn_next, selected_title, image_index, len_images):
    if selected_title.get() == 0 and image_index[0] < len_images-1:
        if image_index[0] == 0:
            btn_prev.configure(state=NORMAL)
        image_index[0] += 1
        change_spinbox(index_spinbox, image_index[0])
        if image_index[0] == len_images-1:
            btn_next.configure(state=DISABLED)
        show_image(image_index[0], track, label_image, index_spinbox, ShowImageMode.SPECTRUM.value)
    if selected_title.get() == 1 and image_index[1] < len_images-1:
        if image_index[1] == 0:
            btn_prev.configure(state=NORMAL)
        image_index[1] += 1
        change_spinbox(index_spinbox, image_index[1])
        if image_index[1] == len_images-1:
            btn_next.configure(state=DISABLED)
        show_image(image_index[1], track, label_image, index_spinbox, ShowImageMode.PROBABILITY.value)

def show_previous_image(track, label_image, index_spinbox, btn_prev, btn_next, selected_title, image_index, len_images):
    if selected_title.get() == 0 and image_index[0] >= 0:
        if image_index[0] == len_images-1:
            btn_next.configure(state=NORMAL)
        image_index[0] -= 1
        change_spinbox(index_spinbox, image_index[0])
        if image_index[0] == 0:
            btn_prev.configure(state=DISABLED)
        show_image(image_index[0], track, label_image, index_spinbox, ShowImageMode.SPECTRUM.value)
    if selected_title.get() == 1 and image_index[1] >= 0:
        if image_index[1] == len_images-1:
            btn_next.configure(state=NORMAL)
        image_index[1] -= 1
        change_spinbox(index_spinbox, image_index[1])
        if image_index[1] == 0:
            btn_prev.configure(state=DISABLED)
        show_image(image_index[1], track, label_image, index_spinbox, ShowImageMode.PROBABILITY.value)

def change_image(track, label_image, index_spinbox, btn_prev, btn_next, selected_title, image_index, len_images):
    if selected_title.get() == 0:
        btn_prev.configure(state=NORMAL)
        btn_next.configure(state=NORMAL)
        image_index[0] = int(index_spinbox.get())
        if int(index_spinbox.get()) == 0:
            btn_prev.configure(state=DISABLED)
        if int(index_spinbox.get()) == len_images-1:
            btn_next.configure(state=DISABLED)
        show_image(image_index[0], track, label_image, index_spinbox, ShowImageMode.SPECTRUM.value)
    if selected_title.get() == 1:
        btn_prev.configure(state=NORMAL)
        btn_next.configure(state=NORMAL)
        image_index[1] = int(index_spinbox.get())
        if int(index_spinbox.get()) == 0:
            btn_prev.configure(state=DISABLED)
        if int(index_spinbox.get()) == len_images-1:
            btn_next.configure(state=DISABLED)
        show_image(image_index[1], track, label_image, index_spinbox, ShowImageMode.PROBABILITY.value)

def details_window_on_closing():
    global btn_show_details_clicked
    global details_window
    btn_show_details_clicked -= 1
    details_window.destroy()

def enter_clicked(event):
    global tab_control
    index_tab = tab_control.tabs().index(tab_control.select())
    if index_tab == 0:
        changed_spinbox_tab1()
    else:
        if index_tab == 1:
            changed_spinbox_tab2()

def show_window_details():
    global btn_show_details_clicked
    btn_show_details_clicked += 1
    if btn_show_details_clicked < 2:
        global details_window
        details_window = Toplevel(main_window)
        details_window.iconbitmap('main_icon.ico')
        details_window.title("Details")
        details_window.resizable(width=False, height=False)
        details_window.bind('<Return>', enter_clicked)
        details_window.protocol("WM_DELETE_WINDOW", details_window_on_closing)

        global tab_control
        tab_control = ttk.Notebook(details_window)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab_control.add(tab1, text=processed_first_track.music_track.short_track_name)
        tab_control.add(tab2, text=processed_second_track.music_track.short_track_name)
        tab_control.add(tab3, text='Divergence')

        global index_of_images
        index_of_images = [[0, 0], [0, 0]]

        label_choose_tab1 = Label(tab1, text="Choose what you want to see:")
        label_choose_tab1.grid(column=0, row=1, sticky=W)

        global selected_title_tab1
        selected_title_tab1 = IntVar()
        rad_notes_spectrum_tab1 = Radiobutton(tab1, text='Notes spectrum', value=0, variable=selected_title_tab1,
                                              command=show_title_tab1)
        rad_notes_spectrum_tab1.grid(column=1, row=1, columnspan=1)
        rad_probability_distribution_tab1 = Radiobutton(tab1, text='Probability distribution', value=1,
                                                        variable=selected_title_tab1, command=show_title_tab1)
        rad_probability_distribution_tab1.grid(column=2, row=1, columnspan=1)

        global label_title_tab1
        label_title_tab1 = Label(tab1, text="Notes spectrum", font=15)
        label_title_tab1.grid(column=1, row=0, sticky=N + S + W + E, pady=(0, 10))

        global btn_previous_tab1
        btn_previous_tab1 = Button(tab1, text="Previous", width=20, command=btn_prev_tab1_clicked)
        btn_previous_tab1.grid(column=0, row=3, pady=5)
        btn_previous_tab1.configure(state=DISABLED)

        global index_spinbox_tab1
        index_spinbox_tab1 = Spinbox(tab1, from_=0, to_=len(processed_first_track.spectral_matrix) - 1,
                                     command=changed_spinbox_tab1)
        index_spinbox_tab1.grid(column=1, row=3, pady=5)

        global btn_next_tab1
        btn_next_tab1 = Button(tab1, text="Next", width=20, command=btn_next_tab1_clicked)
        btn_next_tab1.grid(column=2, row=3, pady=5)

        photoImage1 = PhotoImage(
            file=read_image(index_of_images[0][0], processed_first_track, ShowImageMode.SPECTRUM.value))

        global label_image_tab1
        label_image_tab1 = Label(tab1, image=photoImage1)
        label_image_tab1.grid(column=0, columnspan=3, row=2)

        label_choose_tab2 = Label(tab2, text="Choose what you want to see:")
        label_choose_tab2.grid(column=0, row=1, sticky=W)

        global selected_title_tab2
        selected_title_tab2 = IntVar()
        rad_notes_spectrum_tab2 = Radiobutton(tab2, text='Notes spectrum', value=0, variable=selected_title_tab2,
                                              command=show_title_tab2)
        rad_notes_spectrum_tab2.grid(column=1, row=1, columnspan=1)
        rad_probability_distribution_tab2 = Radiobutton(tab2, text='Probability distribution', value=1,
                                                        variable=selected_title_tab2, command=show_title_tab2)
        rad_probability_distribution_tab2.grid(column=2, row=1, columnspan=1)

        global label_title_tab2
        label_title_tab2 = Label(tab2, text="Notes spectrum", font=15)
        label_title_tab2.grid(column=1, row=0, sticky=N + S + W + E, pady=(0, 10))

        global btn_previous_tab2
        btn_previous_tab2 = Button(tab2, text="Previous", width=20, command=btn_prev_tab2_clicked)
        btn_previous_tab2.grid(column=0, row=3, pady=5)
        btn_previous_tab2.configure(state=DISABLED)

        global index_spinbox_tab2
        index_spinbox_tab2 = Spinbox(tab2, from_=0, to_=len(processed_second_track.spectral_matrix) - 1,
                                     command=changed_spinbox_tab2)
        index_spinbox_tab2.grid(column=1, row=3, pady=5)

        global btn_next_tab2
        btn_next_tab2 = Button(tab2, text="Next", width=20, command=btn_next_tab2_clicked)
        btn_next_tab2.grid(column=2, row=3, pady=5)

        photoImage2 = PhotoImage(
            file=read_image(index_of_images[1][0], processed_second_track, ShowImageMode.SPECTRUM.value))

        global label_image_tab2
        label_image_tab2 = Label(tab2, image=photoImage2)
        label_image_tab2.grid(column=0, columnspan=3, row=2)

        photoImage3 = PhotoImage(
            file=ProcessMusicTrack.ProcessMusicTrack.output_graphic_divergence_of_tracks(processed_first_track, divergence_vec,
                                                                     processed_first_track.music_track.short_track_name,
                                                                     processed_second_track.music_track.short_track_name))
        label_image_tab3 = Label(tab3, image=photoImage3)
        label_image_tab3.grid(column=0, row=0)

        tab_control.pack(expand=1, fill='both')
        details_window.transient(main_window)
        details_window.grab_set()
        details_window.focus_set()
        details_window.wait_window()
        details_window.mainloop()

def modal_window_on_closing():
    print('')

def modal_window_continue_clicked():
    global modal_window
    modal_window.destroy()

def show_modal_window():
    global modal_window
    modal_window = Toplevel(main_window)
    modal_window.iconbitmap('main_icon.ico')
    modal_window.title("Waiting window")
    modal_window.resizable(width=False, height=False)
    modal_window.protocol("WM_DELETE_WINDOW", modal_window_on_closing)

    global image_warning
    label_image_warning = Label(modal_window, image=image_warning)
    label_image_warning.grid(column=0, row=0, pady=5, padx=5)

    label_message = Label(modal_window, text="Start processing! Please, wait...")
    label_message.grid(column=1, row=0, pady=5, padx=5)

    global btn_continue
    btn_continue = Button(modal_window, text="Continue", width=20, command=modal_window_continue_clicked)
    btn_continue.grid(column=0, row=1, columnspan=2, pady=5)
    btn_continue.configure(state=DISABLED)


    modal_window.transient(main_window)
    modal_window.grab_set()
    modal_window.focus_set()
    modal_window.wait_window()
    modal_window.mainloop()

def strart_process(spectrum, filter):
    run_first_track(str(file_first_track), spectrum, filter)
    run_second_track(str(file_second_track), spectrum, filter)

    global created_folder_first_track
    global created_folder_second_track
    created_folder_first_track = True
    created_folder_second_track = True

    global divergence_vec
    global processed_first_track
    global processed_second_track

    divergence_vec, divergence_mean, _ = ProcessMusicTrack.ProcessMusicTrack.get_divergence_of_tracks(
        processed_first_track, processed_second_track)

    label_result.config(text="Result: " + str(round(divergence_mean, 3)))
    btn_show_details.configure(state=NORMAL)
    global btn_continue
    btn_continue.configure(state=NORMAL)

def run_clicked():
    print('Run')
    try:
        spectrum = NONE
        filter = NONE

        print(selected_spectrum.get())
        print(selected_filter.get())

        if selected_spectrum.get() == 0:
            spectrum = ProcessMusicTrack.SpectrumMode.TRANSPOSED_OCTAVE
        else:
            spectrum = ProcessMusicTrack.SpectrumMode.FULL_SPECTRUM
        if selected_filter.get() == 0:
            filter = ProcessMusicTrack.FilterMode.BY_COEFFICIENT
        else:
            filter = ProcessMusicTrack.FilterMode.BY_NUMBER

        global created_folder_first_track
        global created_folder_second_track

        th = threading.Thread(target=strart_process, args=(spectrum, filter,))
        th.start()
        show_modal_window()

    except:
        return

def run_first_track(track_1, spectrum, filter):
    global processed_first_track
    processed_first_track = ProcessMusicTrack.ProcessMusicTrack(track_1, spectrum, filter)
    print(track_1)
    processed_first_track.start_processing()

def run_second_track(track_2, spectrum, filter):
    global processed_second_track
    processed_second_track = ProcessMusicTrack.ProcessMusicTrack(track_2, spectrum, filter)
    print(track_2)
    processed_second_track.start_processing()

def change_rad_main():
    btn_show_details.configure(state=DISABLED)
    label_result.config(text="Result:")

def main_window_on_closing():
    global created_folder_first_track
    global created_folder_second_track
    global file_first_track
    print(str(file_first_track))
    if str(file_first_track) != '' and created_folder_first_track:
        shutil.rmtree(str(file_first_track)[0:len(str(file_first_track)) - 4])
    global file_second_track
    print(str(file_second_track))
    if str(file_second_track) != '' and created_folder_second_track:
        shutil.rmtree(str(file_second_track)[0:len(str(file_second_track)) - 4])
    main_window.destroy()

def show_main_window():
    global main_window
    main_window = Tk()
    main_window.title("Similitary of music tracks")
    main_window.iconbitmap('main_icon.ico')
    main_window.resizable(width=False, height=False)
    main_window.protocol("WM_DELETE_WINDOW", main_window_on_closing)

    global processed_first_track
    global processed_second_track
    global file_first_track
    file_first_track = ''
    global file_second_track
    file_second_track = ''
    global image_warning
    image_warning = PhotoImage(file='warning.png')

    global label_first_track
    label_first_track = Label(main_window, text="Music track №1")
    label_first_track.grid(column=0, row=0, pady=5, padx=5)

    global txt_first_track_name
    txt_first_track_name = Entry(main_window, state="normal")
    txt_first_track_name.grid(column=1, row=0, columnspan=2, sticky=N+S+W+E, pady=5)
    txt_first_track_name.configure(state=DISABLED)

    global btn_choose_first_track
    btn_choose_first_track = Button(main_window, text="Choose track №1", command=first_track_button_clicked)
    btn_choose_first_track.grid(column=3, row=0, sticky=N+S+W+E, pady=5, padx=5)

    global label_second_track_name
    label_second_track_name = Label(main_window, text="Music track №2")
    label_second_track_name.grid(column=0, row=1, pady=5, padx=5)

    global txt_second_track_name
    txt_second_track_name = Entry(main_window, width=10, state="normal")
    txt_second_track_name.grid(column=1, row=1, columnspan=2, sticky=N+S+W+E, pady=5)
    txt_second_track_name.configure(state=DISABLED)

    global btn_choose_second_track
    btn_choose_second_track = Button(main_window, text="Choose track №2", command=second_track_button_clicked)
    btn_choose_second_track.grid(column=3, row=1, pady=5, padx=5)

    global label_filter_radiobutton
    label_filter_radiobutton = Label(main_window, text="Filtration method: ")
    label_filter_radiobutton.grid(column=0, row=2, pady=(30,5), padx=5, sticky=W)

    global selected_filter
    selected_filter = IntVar()
    print(selected_filter.get())
    rad_filter_thresold = Radiobutton(main_window, text='Threshold filtering', value=0, variable=selected_filter, command=change_rad_main)
    rad_filter_thresold.grid(column=1, row=2, columnspan=1, pady=(30,5), padx=5)
    rad_filter_number = Radiobutton(main_window, text='Filtering by number', value=1, variable=selected_filter, command=change_rad_main)
    rad_filter_number.grid(column=2, row=2, columnspan=1, pady=(30,5), padx=5)

    global label_spectrum_radiobutton
    label_spectrum_radiobutton = Label(main_window, text="Spectrum: ")
    label_spectrum_radiobutton.grid(column=0, row=3, pady=5, padx=5, sticky=W)

    global selected_spectrum
    selected_spectrum = IntVar()
    print(selected_spectrum.get())
    rad_transposed = Radiobutton(main_window, text='Transposed octave', value=0, variable=selected_spectrum, command=change_rad_main)
    rad_transposed.grid(column=1, row=3, columnspan=1, pady=5, padx=5)
    rad_full_spectrum = Radiobutton(main_window, text='Full spectrum', value=1, variable=selected_spectrum, command=change_rad_main)
    rad_full_spectrum.grid(column=2, row=3, columnspan=1, pady=5, padx=5)

    global btn_run
    btn_run = Button(main_window, text="Run", command=run_clicked)
    btn_run.grid(column=3, row=4, sticky=N+S+W+E, pady=(30,5), padx=5)
    btn_run.configure(state=DISABLED)

    global label_result
    label_result = Label(main_window, text="Result:")
    label_result.grid(column=0, row=4, rowspan=2, sticky=W, pady=(30,5), padx=5)

    global btn_show_details
    global btn_show_details_clicked
    btn_show_details_clicked = 0
    btn_show_details = Button(main_window, text="Show details", command=show_window_details)
    btn_show_details.grid(column=3, row=5, sticky=N+S+W+E, pady=5, padx=5)
    btn_show_details.configure(state=DISABLED)

    main_window.mainloop()

if __name__ == '__main__':
    show_main_window()