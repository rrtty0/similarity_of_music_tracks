import math
from scipy.fft import rfft, rfftfreq
import statistics
from enum import Enum
import os
import numpy as np
import matplotlib.pyplot as plt
import musicTrack as mt


class SpectrumMode(Enum):
    FULL_SPECTRUM = 'Full spectrum'
    TRANSPOSED_OCTAVE = 'Transposed octave'


class FilterMode(Enum):
    BY_COEFFICIENT = 'Filter by coefficient'
    BY_NUMBER = 'Filter by number'


class ProcessMusicTrack():
    F0 = 220
    FRAME_SIZE = 8192
    THRESHOLD_OF_NOISE = 0.25
    NUMBER_OF_NOTES = 60
    NUMBER_OF_GOOD_FRAMES = 60
    SAMPLE_RATE = 44100
    NUMBER_OF_NOTES_AT_OCTAVE = 12
    NUMBER_OF_OCTAVES = 5
    STEP_FOR_DISTRIBUTION_DENSITY_OF_NOTES = 0.1
    LOWER_DENSITY_LIMIT = 0.0001
    SPECTRUM_MODE = None
    FILTER_MODE = None


    def __init__(self, path_to_track, spectrum_mode, filter_mode):
        self.music_track = mt.MusicTrack(path_to_track)
        self.output_directory = path_to_track[0:len(path_to_track)-4]
        self.numberOfFrames = -1
        self.frames = []
        self.fourier_frames = []
        self.frequencies = []
        self.notes_indexes = []
        self.notes_environments = []
        self.spectral_matrix = []
        self.distribution_density_for_notes = []
        ProcessMusicTrack.SPECTRUM_MODE = spectrum_mode.value
        ProcessMusicTrack.FILTER_MODE = filter_mode.value

    def filter_frames_by_coefficient(self, log):
        frames = []
        for i in range(self.numberOfFrames):
            frame = np.abs(self.music_track.music_data[ProcessMusicTrack.FRAME_SIZE * i:ProcessMusicTrack.FRAME_SIZE * (i + 1)])
            if log:
                print('frame #' + str(i))
                print('start point: ' + str(ProcessMusicTrack.FRAME_SIZE * i))
                print('finish point: ' + str(ProcessMusicTrack.FRAME_SIZE * (i + 1) - 1))
                print('len: ' + str(len(frame)))
                print('mean: ' + str(np.mean(frame)) + '\n')
            if np.mean(frame) >= ProcessMusicTrack.THRESHOLD_OF_NOISE * self.music_track.middleValue:
                frame = self.music_track.music_data[ProcessMusicTrack.FRAME_SIZE * i:ProcessMusicTrack.FRAME_SIZE * (i + 1)]
                frames += [frame]

        return frames

    def filter_frames_by_number(self, log):
        frames = []
        indexes_and_means_of_good_frames = {a * -1: a * -1 for a in range(1, ProcessMusicTrack.NUMBER_OF_GOOD_FRAMES + 1)}

        for i in range(self.numberOfFrames):
            frame = np.abs(self.music_track.music_data[ProcessMusicTrack.FRAME_SIZE * i:ProcessMusicTrack.FRAME_SIZE * (i + 1)])
            if log:
                print('frame #' + str(i))
                print('start point: ' + str(ProcessMusicTrack.FRAME_SIZE * i))
                print('finish point: ' + str(ProcessMusicTrack.FRAME_SIZE * (i + 1) - 1))
                print('len: ' + str(len(frame)))
                print('mean: ' + str(np.mean(frame)) + '\n')
            self.check_frame(indexes_and_means_of_good_frames, frame, i)

        print('Good frames:\n' + str(indexes_and_means_of_good_frames))

        for index, value in indexes_and_means_of_good_frames.items():
            frame = self.music_track.music_data[ProcessMusicTrack.FRAME_SIZE * index:ProcessMusicTrack.FRAME_SIZE * (index + 1)]
            frames += [frame]

        return frames

    def check_frame(self, indexes_and_means_of_good_frames, frame, index_of_frame):
        index_of_min_value, min_value = self.find_min(indexes_and_means_of_good_frames)
        if np.mean(frame) > min_value:
            indexes_and_means_of_good_frames.pop(index_of_min_value)
            indexes_and_means_of_good_frames[index_of_frame] = np.mean(frame)

    def find_min(self, indexes_and_means_of_good_frames):
        list_of_data = list(indexes_and_means_of_good_frames.items())
        min_k = list_of_data[0][0]
        min_v = list_of_data[0][1]
        for k, v in indexes_and_means_of_good_frames.items():
            if v < min_v:
                min_k = k
                min_v = v

        return min_k, min_v

    def fourier_transformation(self, log):
        fourier_frames = []

        xf = rfftfreq(ProcessMusicTrack.FRAME_SIZE, 1 / ProcessMusicTrack.SAMPLE_RATE)
        for i in range(len(self.frames)):
            yf = rfft(self.frames[i])
            fourier_frames = fourier_frames + [np.abs(yf)]

        if log:
            print('Number of Fourier frames: ' + str(len(fourier_frames)))
            print('Length of Fourier frames: ' + str(len(fourier_frames[0])))
            print('Length of Fourier frames: ' + str(len(fourier_frames[len(fourier_frames) - 1])))
            print('Length of xf: ' + str(len(xf)))
            print('xf: ' + str(xf))

        return fourier_frames, xf

    def make_notes(self, log):
        notes_indexes = []
        notes_environments = []

        for i in range(ProcessMusicTrack.NUMBER_OF_NOTES):
            delta = 100000
            freq = -1
            index = -1
            fi = ProcessMusicTrack.F0 * (2 ** (i / 12))
            for current_index in range(len(self.frequencies)):
                if abs(self.frequencies[current_index] - fi) <= delta:
                    delta = abs(self.frequencies[current_index] - fi)
                    freq = self.frequencies[current_index]
                    index = current_index
                else:
                    break

            notes_indexes.append(index)

            if i > 0:
                middle = (self.frequencies[index] + self.frequencies[notes_indexes[len(notes_indexes) - 2]]) / 2
                k = notes_indexes[len(notes_indexes) - 2]
                while middle >= self.frequencies[k]:
                    k += 1
                notes_environments[i - 1].append(k - 1)
                notes_environments.append([k])
                if i == ProcessMusicTrack.NUMBER_OF_NOTES - 1:
                    k = index
                    while self.frequencies[index] + self.frequencies[index] - middle >= self.frequencies[k]:
                        k += 1
                    notes_environments[i].append(k - 1)

                    middle = (self.frequencies[notes_indexes[0]] + self.frequencies[notes_indexes[1]]) / 2
                    k = notes_indexes[0]
                    while (self.frequencies[notes_indexes[0]] - (middle - self.frequencies[notes_indexes[0]])) < self.frequencies[k]:
                        k -= 1
                    notes_environments[0].append(notes_environments[0][0])
                    notes_environments[0][0] = k + 1
            else:
                notes_environments.append([])

            if log:
                print('--------------------------')
                print('i: ' + str(i))
                print('fi: ' + str(fi) + ' or 220*2^(' + str(i) + '/12)')
                print('delta: ' + str(delta))
                print('freq: ' + str(freq))
                print('index: ' + str(index))
                print('xf[index]: ' + str(self.frequencies[index]))
                print('xf[index - 1]: ' + str(self.frequencies[index - 1]))
                print('xf[index + 1]: ' + str(self.frequencies[index + 1]))

        return notes_indexes, notes_environments

    def print_notes(self):
        for i in range(ProcessMusicTrack.NUMBER_OF_NOTES):
            print('-------------------')
            print('Note number: ' + str(i))
            print('Index of note: ' + str(self.notes_indexes[i]))
            print('Note frequency: ' + str(self.frequencies[self.notes_indexes[i]]))
            print('Indexes of note environment: ' + str(self.notes_environments[i]))
            print('Frequencies of note environment: [' + str(self.frequencies[self.notes_environments[i][0]]) + ', ' + str(
                self.frequencies[self.notes_environments[i][1]]) + ']')
            print('delta left: ' + str(self.notes_indexes[i] - self.notes_environments[i][0]))
            print('delta right: ' + str(self.notes_environments[i][1] - self.notes_indexes[i]))
            if i != 0:
                print('delta delta: ' + str(abs((self.notes_environments[i - 1][1] - self.notes_indexes[i - 1]) - (
                            self.notes_indexes[i] - self.notes_environments[i][0]))))

    def make_matrix_of_full_spectrum(self):
        matrix = []
        for frame in self.fourier_frames:
            matrix.append([])
            for note_environment in self.notes_environments:
                note_mid = np.mean(frame[note_environment[0]:note_environment[1] + 1])
                matrix[len(matrix) - 1].append(note_mid)
            matrix[len(matrix) - 1] /= max(matrix[len(matrix) - 1])

        return matrix

    def make_matrix_of_transposed_octave(self):
        matrix = []
        for frame in self.fourier_frames:
            matrix.append([])
            for note_number in range(ProcessMusicTrack.NUMBER_OF_NOTES_AT_OCTAVE):
                notes_mid = []
                for octave_number in range(ProcessMusicTrack.NUMBER_OF_OCTAVES):
                    notes_mid.append(np.mean(frame[self.notes_environments[
                                                       octave_number * self.NUMBER_OF_NOTES_AT_OCTAVE + note_number][0]:
                                                   self.notes_environments[
                                                       octave_number * self.NUMBER_OF_NOTES_AT_OCTAVE + note_number][
                                                       1] + 1]))
                matrix[len(matrix) - 1].append(np.mean(notes_mid))
            matrix[len(matrix) - 1] /= max(matrix[len(matrix) - 1])

        return matrix

    def output_to_file_spectral_matrix(self):
        name_of_file = self.output_directory + '\\' + ' SPECTRAL_MATRIX ' + ' - ' + str(ProcessMusicTrack.FILTER_MODE)\
                       + ' - ' + str(ProcessMusicTrack.SPECTRUM_MODE) + '.txt'
        f = open(name_of_file, 'w')
        for i in range(len(self.spectral_matrix)):
            for j in range(len(self.spectral_matrix[i])):
                if j % 10 == 0 and j != 0:
                    f.write('\n')
                f.write(str(round(self.spectral_matrix[i][j], 4)) + '\t')
            f.write('\n\n')
        f.close()

    def output_to_file_distribution_density(self):
        name_of_file = self.output_directory + '\\' + ' DENSITY ' + ' - ' + str(ProcessMusicTrack.FILTER_MODE) \
                       + ' - ' + str(ProcessMusicTrack.SPECTRUM_MODE) + '.txt'
        f = open(name_of_file, 'w')
        for i in range(len(self.distribution_density_for_notes)):
            for j in range(len(self.distribution_density_for_notes[i])):
                if j % 10 == 0 and j != 0:
                    f.write('\n')
                f.write(str(round(self.distribution_density_for_notes[i][j], 4)) + '\t')
            f.write('\n\n')
        f.close()

    def output_graphic_of_spectral_matrix(self, frame_index):
        if not os.path.exists(self.output_directory + '\\' + 'Notes spectrum'):
            os.mkdir(self.output_directory + '\\' + 'Notes spectrum')

        fig, ax = plt.subplots()
        ax.set_title('Relation function amplitude value of note\n' + self.music_track.short_track_name + ' (frame #' +
                     str(frame_index) + ')', fontsize=12)
        ax.set_xlabel('Note Number')
        ax.set_ylabel('Amplitude')
        ax.plot([c for c in range(len(self.spectral_matrix[frame_index]))], self.spectral_matrix[frame_index])
        fig.savefig(self.output_directory + '\\' + 'Notes spectrum' + '\\' + 'Notes_spectrum_frame #' + str(
            frame_index) + '.png')

        return self.output_directory + '/' + 'Notes spectrum' + '/' + 'Notes_spectrum_frame #' + str(
            frame_index) + '.png'

    def output_graphic_of_probability_distribution(self, frame_index):
        if not os.path.exists(self.output_directory + '\\' + 'Probability distribution'):
            os.mkdir(self.output_directory + '\\' + 'Probability distribution')

        x = [str(round(s, 2)) + ' - ' + str(round(s + ProcessMusicTrack.STEP_FOR_DISTRIBUTION_DENSITY_OF_NOTES, 2)) for
             s in
             np.arange(0, 1, ProcessMusicTrack.STEP_FOR_DISTRIBUTION_DENSITY_OF_NOTES)]
        y = self.distribution_density_for_notes[frame_index]

        fig, ax = plt.subplots()
        ax.bar(x, y)

        ax.set_title('Probability distribution\n' + self.music_track.short_track_name + ' (frame #' + str(frame_index) +
                     ')', fontsize=12)
        ax.set_xlabel('Ranges')
        ax.set_ylabel('Value of probabitity')

        ax.set_facecolor('seashell')
        fig.set_facecolor('floralwhite')
        fig.set_figwidth(9)  # ширина Figure
        fig.set_figheight(5)  # высота Figure

        fig.savefig(self.output_directory + '\\' + 'Probability distribution' + '\\' +
                    'Probability_distribution_frame #' + str(frame_index) + '.png')

        return self.output_directory + '/' + 'Probability distribution' + '/' + \
               'Probability_distribution_frame #' + str(frame_index) + '.png'

    def output_graphic_divergence_of_tracks(self, divergence, str1, str2):
        if not os.path.exists(self.output_directory + '\\' + 'Divergence'):
            os.mkdir(self.output_directory + '\\' + 'Divergence')

        fig, ax = plt.subplots()
        x = [c for c in range(len(divergence))]
        ax.plot(x, divergence, label='Divergence')
        ax.plot(x, [np.mean(divergence) for c in range(len(divergence))],
                label='Mean(Divergence)=' + str(round(np.mean(divergence), 3)))
        ax.plot(x, [statistics.median(divergence) for c in range(len(divergence))],
                label='Median(Divergence)=' + str(round(statistics.median(divergence), 3)))

        ax.set_title(str(ProcessMusicTrack.SPECTRUM_MODE) + ' and ' + str(
            ProcessMusicTrack.FILTER_MODE) + '\n' + 'Divergence' + '\n' + str1 + '  -  ' + str2, fontsize=10)
        ax.set_xlabel('Note Number')
        ax.set_ylabel('Divergence')

        ax.legend()

        fig.savefig(self.output_directory + '\\' + 'Divergence' + '\\' + 'Result divergence.png')

        return self.output_directory + '/' + 'Divergence' + '/' + 'Result divergence.png'

    def get_distribution_density_for_notes(self):
        distribution_density_for_notes = []
        for j in range(len(self.spectral_matrix[0])):
            distribution_density_for_note = [0 for c in range(int(1 / ProcessMusicTrack.STEP_FOR_DISTRIBUTION_DENSITY_OF_NOTES))]
            for i in range(len(self.spectral_matrix)):
                if self.spectral_matrix[i][j] != 1:
                    distribution_density_for_note[int(self.spectral_matrix[i][j] // ProcessMusicTrack.STEP_FOR_DISTRIBUTION_DENSITY_OF_NOTES)] += 1
                else:
                    distribution_density_for_note[len(distribution_density_for_note) - 1] += 1
            distribution_density_for_note = [el / len(self.spectral_matrix) for el in distribution_density_for_note]
            distribution_density_for_notes.append(distribution_density_for_note)

        return distribution_density_for_notes

    def show_distribution_density_for_note(self, index):
        x = [str(round(s, 2)) + ' - ' + str(round(s + ProcessMusicTrack.STEP_FOR_DISTRIBUTION_DENSITY_OF_NOTES, 2)) for s in
             np.arange(0, 1, ProcessMusicTrack.STEP_FOR_DISTRIBUTION_DENSITY_OF_NOTES)]
        y = self.distribution_density_for_notes[index]

        fig, ax = plt.subplots()
        ax.bar(x, y)

        ax.set_title('Probability distribution', fontsize=12)
        ax.set_xlabel('Ranges')
        ax.set_ylabel('Value of probabitity')

        ax.set_facecolor('seashell')
        fig.set_facecolor('floralwhite')
        fig.set_figwidth(15)  # ширина Figure
        fig.set_figheight(6)  # высота Figure

        plt.show()

    def start_processing(self):
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)
        self.music_track.prepare_data(ProcessMusicTrack.SAMPLE_RATE)
        self.music_track.load_music_data(ProcessMusicTrack.SAMPLE_RATE)
        self.numberOfFrames = self.music_track.supplement_signal(ProcessMusicTrack.FRAME_SIZE)

        if ProcessMusicTrack.FILTER_MODE == FilterMode.BY_NUMBER.value:
            self.frames = self.filter_frames_by_number(False)
        else:
            self.frames = self.filter_frames_by_coefficient(False)
        print('Number of good frames: ' + str(len(self.frames)))
        print('Length of frames: ' + str(len(self.frames[0])))
        print('-----------------------------------------------')

        self.fourier_frames, self.frequencies = self.fourier_transformation(False)
        self.notes_indexes, self.notes_environments = self.make_notes(False)
        #self.print_notes()
        print('--------------------------------------------------------')

        if ProcessMusicTrack.SPECTRUM_MODE == SpectrumMode.FULL_SPECTRUM.value:
            self.spectral_matrix = self.make_matrix_of_full_spectrum()
        else:
            self.spectral_matrix = self.make_matrix_of_transposed_octave()
        print('Number of matrixes rows: ' + str(len(self.spectral_matrix)))
        print('Number of matrixes columns: ' + str(len(self.spectral_matrix[0])))
        self.output_to_file_spectral_matrix()

        self.distribution_density_for_notes = self.get_distribution_density_for_notes()
        self.output_to_file_distribution_density()

    def get_Kullback_Leibler_divergence(self, second_track):
        kullback_leibler_divergencies = []
        for i in range(len(self.distribution_density_for_notes)):
            divergence=0
            for j in range(len(self.distribution_density_for_notes[i])):
                q = second_track.distribution_density_for_notes[i][j]
                if second_track.distribution_density_for_notes[i][j] == 0:
                    q = ProcessMusicTrack.LOWER_DENSITY_LIMIT
                if self.distribution_density_for_notes[i][j] != 0:
                    divergence += self.distribution_density_for_notes[i][j]*math.log2(self.distribution_density_for_notes[i][j] / q)

            kullback_leibler_divergencies.append(divergence)

        return kullback_leibler_divergencies

    @staticmethod
    def show_divergence(str1, str2, divergence, name_of_divergence):
        print('\n' + name_of_divergence + ' ' + str1 + ' of ' + str2 + ':')
        print('Mean: ' + str(np.mean(divergence)))
        print('Median: ' + str(statistics.median(divergence)))
        print(name_of_divergence + ': ' + str(divergence))

        fig, ax = plt.subplots()
        x = [c for c in range(len(divergence))]
        ax.plot(x, divergence, label='Divergence')
        ax.plot(x, [np.mean(divergence) for c in range(len(divergence))],
                label='Mean(Divergence)=' + str(round(np.mean(divergence), 3)))
        ax.plot(x, [statistics.median(divergence) for c in range(len(divergence))],
                label='Median(Divergence)=' + str(round(statistics.median(divergence), 3)))

        ax.set_title(str(ProcessMusicTrack.SPECTRUM_MODE) + ' and ' + str(
            ProcessMusicTrack.FILTER_MODE) + '\n' + name_of_divergence + '\n' + str1 + '  -  ' + str2, fontsize=10)
        ax.set_xlabel('Note Number')
        ax.set_ylabel(name_of_divergence)

        ax.legend()
        plt.show()

        # fig.savefig(self.output_directory + '\\' + name_of_divergence + ' ' + str1 + '-' + str2 + '.png')

    @staticmethod
    def get_mean_of_divergencies(first_divergence, second_divergence):
        mean_of_divergencies = []
        for i in range(len(first_divergence)):
            mean_of_divergencies.append(np.mean([first_divergence[i], second_divergence[i]]))

        return mean_of_divergencies

    @staticmethod
    def get_divergence_of_tracks(track1, track2):
        first_divergence = track1.get_Kullback_Leibler_divergence(track2)
        second_divergence = track2.get_Kullback_Leibler_divergence(track1)
        # PrMusTr.show_divergence(track1.music_track.short_track_name,
        #                                  track2.music_track.short_track_name, first_divergence, 'K-L Divergence')
        # PrMusTr.show_divergence(track2.music_track.short_track_name,
        #                                  track1.music_track.short_track_name, second_divergence, 'K-L Divergence')
        mean_of_divergencies = ProcessMusicTrack.get_mean_of_divergencies(first_divergence, second_divergence)
        # PrMusTr.show_divergence(track1.music_track.short_track_name,
        #                                  track2.music_track.short_track_name, mean_of_divergencies, 'Divergence of tracks')

        return [mean_of_divergencies, np.mean(mean_of_divergencies), statistics.median(mean_of_divergencies)]