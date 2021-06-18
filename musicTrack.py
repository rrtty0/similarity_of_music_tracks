import librosa.display
from pydub import AudioSegment
import re
import soundfile
import matplotlib.pyplot as plt
import sys
import numpy as np


# Класс музыкальной композиции
class MusicTrack():

    # Создает объект музыкального трека по умолчанию
    # self - объект класса
    # path_to_track - путь к файлу
    def __init__(self, path_to_track):
        self.track_name = path_to_track
        self.short_track_name = re.search(r'[^/]*\.[^/]{1,}$', str(path_to_track)).group(0)

    # Конвертирует музыкальный трек в формат wav из mp3
    # self - объект класса
    # track_name_mp3 - имя mp3 трека
    # return - путь к wav файлу трека
    def mp3_to_wav(self, track_name_mp3):
        result = re.search(r'[^/]*\.mp3$', track_name_mp3)
        track_name_wav = result.group(0)[0:len(result.group(0)) - 3] + 'wav'

        sound = AudioSegment.from_mp3(track_name_mp3)
        path_to_export = track_name_mp3[0:len(track_name_mp3)-4] + '\\' + track_name_wav
        sound.export(path_to_export, format='wav')

        return path_to_export

    # Конвертирует музыкальный трек в формат wav из ogg
    # self - объект класса
    # track_name_ogg - имя ogg трека
    # return - путь к wav файлу трека
    def ogg_to_wav(self, track_name_ogg, sample_rate):
        result = re.search(r'[^/]*\.ogg$', track_name_ogg)
        track_name_wav = result.group(0)[0:len(result.group(0)) - 3] + 'wav'

        sound_data, _ = soundfile.read(track_name_ogg)
        path_to_export = track_name_ogg[0:len(track_name_ogg) - 4] + '\\' + track_name_wav
        soundfile.write(path_to_export, sound_data, sample_rate)

        return path_to_export

    # Определение формата входного трека и его преобразование
    # self - объект класса
    # return - пустое значение
    def prepare_data(self, sample_rate):
        result = re.search(r'\.mp3$', self.track_name)
        if result:
            print('Type of file: MP3')
            self.track_name = self.mp3_to_wav(self.track_name)
            return
        else:
            result = re.search(r'\.wav$', self.track_name)
            if result:
                print('Type of file: WAV')
                self.track_name = self.track_name
                return
            else:
                result = re.search(r'\.ogg$', self.track_name)
                if result:
                    print('Type of file: OGG')
                    self.track_name = self.ogg_to_wav(self.track_name, sample_rate)
                    return
                else:
                    print('ERROR: Unknown type of file')

        sys.exit()

    # Рисование графика сигнала во временной области
    # self - объект класса
    # music_data - музыкальное произведение
    # music_data - частота дискретизации
    # return - None
    def monophonic_graphic(self, music_data, sr):
        plt.figure(figsize=(7, 5))
        librosa.display.waveplot(music_data, sr=sr)
        plt.title('Monophonic')
        plt.show()

    # Загрузка данных музыкального произвдения
    # self - объект класса
    # return - None
    def load_music_data(self, sample_rate):
        self.music_data, sr = librosa.load(self.track_name, sr=sample_rate)
        self.music_data = librosa.to_mono(self.music_data)
        print('Length of track at points: ' + str(len(self.music_data)))
        print('Sampling frequency: ' + str(sr))
        #self.monophonic_graphic(self.music_data, sr)

        self.middleValue = np.mean(np.abs(self.music_data))
        print('Middle value module of signal: ' + str(self.middleValue))

    # Доопределение сигнала нулями
    # self - объект класса
    # return - Сиглнал, доопеределенный нулями
    def supplement_signal(self, frame_size):
        self.music_data = list(self.music_data) + list([c * 0 for c in range(frame_size - (len(self.music_data)
                                             - frame_size * (len(self.music_data) // frame_size)))])
        print('Length of track at points after supplement: ' + str(len(self.music_data)))
        numberOfFrames = int(len(self.music_data) / frame_size)
        print('Number of frames: ' + str(numberOfFrames) + '\n')

        return numberOfFrames