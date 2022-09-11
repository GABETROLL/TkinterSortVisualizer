import tkinter
import sounddevice
import numpy
# for audio
from threading import Thread
from time import sleep
# for core
from algorithms import *
from itertools import chain
# for controlling core
from colorsys import hsv_to_rgb
# for display


def rainbow_color(num: int, max_num: int):
    try:
        hue = num / max_num
    except ZeroDivisionError:
        hue = 0

    r, g, b = hsv_to_rgb(hue, 1, 1)

    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)

    return '#%02x%02x%02x' % (r, g, b)


class SortControl(Thread, SortPlayground):
    """Container for all sorts, settings and shuffles.
    Runs loop with algorithm coroutines during the main window mainloop.
    Controls playing and pausing."""

    def __init__(self, main_array_len: int, delay: float):
        Thread.__init__(self)
        SortPlayground.__init__(self, main_array_len)

        self.delay = delay

        self.sorts = {c.__doc__: c(self) for c in sorts}
        self.sort_name = "Bubble Sort"
        self.inputs = {c.__doc__: c(self) for c in inputs}
        self.input_name = "Random Input"
        self.shuffles = {c.__doc__: c(self) for c in shuffles}
        self.shuffle_name = "Nothing"
        self.verify_algorithm = Verify(self)
        # Settings chosen by UI.

        self.chosen_algorithms = iter(())
        # chain of all chosen algorithms
        self.reset()
        # define chain

        self.exited = False
        self.playing = False
        # data

    def reset(self):
        """Resets self.chosen_algorithms and resets self as SortPlayground."""
        self.chosen_algorithms = chain(self.inputs[self.input_name].run(),
                                       self.shuffles[self.shuffle_name].run(),
                                       self.sorts[self.sort_name].run(),
                                       self.verify_algorithm.run())
        SortPlayground.reset(self)

    def stop(self):
        self.playing = False
        self.reset()
        # To refresh coroutines when they end.

    def pause_play(self):
        self.playing = not self.playing

    def change_delay(self, s: float):
        self.delay = s

    def choose_input(self, name: str):
        if not (name in self.inputs):
            raise KeyError(f"Input '{name}' doesn't exist.")
        self.input_name = name

        self.stop()
        # restart

    def choose_shuffle(self, name: str):
        if not (name in self.shuffles):
            raise KeyError(f"Shuffle '{name}' doesn't exist.")
        self.shuffle_name = name

        self.stop()
        # restart

    def choose_sort(self, name: str):
        if not (name in self.sorts):
            raise KeyError(f"Sort '{name}' doesn't exist.")
        self.sort_name = name

        self.stop()
        # restart

    def exit(self):
        self.exited = True

    def run(self):
        while not self.exited:

            if self.playing:
                try:
                    next(self.chosen_algorithms)
                except StopIteration:
                    self.stop()

            sleep(self.delay)


class AudioControl(sounddevice.OutputStream):
    """OutputStream of frequencies representing nums in SortControl"""
    def __init__(self, sort_control: SortControl, octaves: int):
        self.lowest = 210
        sounddevice.OutputStream.__init__(self, blocksize=self.lowest, channels=1, callback=self.callback)
        # 210 divides 44100 evenly.
        # Should also match the harmonics of the lowest note.

        self.sort_control = sort_control

        self.octaves = octaves

        self.frequencies = {}
        # frequency: start_index

        self.start()

    @property
    def minimum_duration(self):
        """Shortest wave has to be long enough to
        be audible as an individual note."""
        return self.blocksize * 2
    # going past 8 gives an underrun...

    @property
    def duration(self):
        """Duration of each note in frames."""
        # 1 -> self.sample_rate
        # 0 -> self.minimum_duration
        # Length of note decreases linearly: max is one second (self.samplerate samples)
        # and min is self.minimum_duration.
        return (self.samplerate - self.minimum_duration) * self.sort_control.delay + self.minimum_duration

    def frequency(self, num: int):
        result = self.lowest * (2 ** self.octaves) ** (num / self.sort_control.main_array_len)
        return result
        # equal temperament using self.sort_control.max as the number of notes per self.octaves octaves.

    def audify(self):
        """Changes the current frequency played."""
        if not self.sort_control.playing:
            self.frequencies = {}
            return

        # stopped, playing, frequencies, new_frequencies:
        #   True     False      []             []
        #   False    True       []            [...]
        #   False    True      [...]          [...]
        #   False    True      [...]           []

        for num in self.sort_control.read_at_pointers():
            frequency = self.frequency(num)
            # To display the num as a proportional frequency

            self.frequencies.setdefault(frequency, 0)
            # Each frequency has a current index in the wave.

    def sine_waves(self, frames: int):
        # frames of audio controller
        """Returns sine_waves of all nums currently pointed at by self.sort_control
        as added sine waves."""
        result = numpy.zeros((frames, 1))

        for frequency, start_index in self.frequencies.copy().items():
            for frame_count in range(frames):
                wave_index = start_index + frame_count
                input_index = wave_index * 2 * numpy.pi * frequency / self.samplerate

                amplitude = (self.duration - wave_index) / self.duration
                # each note fades out

                result[frame_count] += amplitude * numpy.sin(input_index)

                if amplitude <= 0:
                    self.frequencies.pop(frequency)
                    break
            else:
                self.frequencies[frequency] += frames

        return result

    def callback(self, outdata: numpy.ndarray, frames: int, time, status) -> None:
        """writes sound output to 'outdata' Called by self in sounddevice.OutputStream."""
        # params may need annotations... :/
        self.audify()
        outdata[:] = self.sine_waves(frames)


class SortApp(tkinter.Tk):
    def __init__(self, sort_control: SortControl):
        tkinter.Tk.__init__(self)

        self.sort_control = sort_control

        self.audio_control = AudioControl(self.sort_control, 4)

        self.canvas = tkinter.Canvas(self, width=1024, height=512)
        self.canvas.pack()

        self.play = tkinter.Button(self, text=self.play_text, command=self.sort_control.pause_play)
        self.play.pack()

        self.settings_button = tkinter.Button(self, text="Sorts/Shuffles", command=self.goto_settings)
        self.settings_button.pack()

        self.sort_variable = tkinter.StringVar(self, "Bubble Sort")
        self.input_variable = tkinter.StringVar(self, "Random Input")
        self.shuffle_variable = tkinter.StringVar(self, "Nothing")

        self.size_variable = tkinter.IntVar(self, self.sort_control.main_array_len)
        self.choosing_sort = False
        # PLEASE ALLOW USER TO SCRAMBLE FREELY BY COMBINING SHUFFLES AND INPUTS.

        self.min_delay = 0
        self.max_delay = 1
        self.display_factor = 12
        self.log_factor = 2 ** (1 / self.display_factor)
        # in seconds
        self.speed_control = tkinter.Scale(self,
                                           from_=self.max_delay * self.display_factor,
                                           to=self.min_delay,
                                           orient=tkinter.HORIZONTAL)
        # 1s delay to 0s delay mapped as 1023 -> 0
        self.speed_control.pack()

    @property
    def play_text(self):
        return "pause" if self.sort_control.playing else "play"

    def control_speed(self):
        visual_delay = int(self.speed_control.get())
        base = 2
        delay = (base ** visual_delay - 1) / (base ** self.display_factor - 1)
        # It's easier to slide the speed Scale when speeds are exponential.

        self.sort_control.change_delay(delay)

    def display(self):
        self.play.config(text=self.play_text)

        self.canvas.delete("all")

        bar_width = self.canvas.winfo_width() / (self.sort_control.main_array_len + 1)
        max_height = self.canvas.winfo_height() / self.sort_control.array_count

        for array_index, array in enumerate(self.sort_control.arrays):

            for num_index, num in enumerate(array):
                try:
                    height = max_height * num / self.sort_control.main_array_len
                except ZeroDivisionError:
                    height = 0

                x0 = num_index * bar_width
                x1 = x0 + bar_width

                y0 = max_height * array_index

                color = "black" if (array_index, num_index) in self.sort_control.pointers else \
                    rainbow_color(num, self.sort_control.main_array_len)

                self.canvas.create_rectangle(x0,
                                             y0,
                                             x1,
                                             y0 + height,
                                             fill=color,
                                             outline=color)
        self.canvas.update()

    def clear_screen(self):
        for child in self.winfo_children():
            child.pack_forget()

    def exit_settings(self):
        self.clear_screen()
        self.choosing_sort = False

        sort_name = self.sort_variable.get()
        self.sort_control.choose_sort(sort_name)

        input_name = self.input_variable.get()
        self.sort_control.choose_input(input_name)

        shuffle_name = self.shuffle_variable.get()
        self.sort_control.choose_shuffle(shuffle_name)

        self.sort_control.change_main_array_len(self.size_variable.get())

        self.canvas.pack()
        self.play.pack()
        self.speed_control.pack()
        self.settings_button.pack()

    def goto_settings(self):
        self.clear_screen()

        self.choosing_sort = True

        sort_names = self.sort_control.sorts.keys()
        tkinter.OptionMenu(self, self.sort_variable, self.sort_variable.get(), *sort_names).pack()

        input_names = self.sort_control.inputs.keys()
        tkinter.OptionMenu(self, self.input_variable, self.input_variable.get(), *input_names).pack()

        shuffle_names = self.sort_control.shuffles.keys()
        tkinter.OptionMenu(self, self.shuffle_variable, self.shuffle_variable.get(), *shuffle_names).pack()

        tkinter.Scale(self, from_=4, to=1024, variable=self.size_variable, length=1024, orient=tkinter.HORIZONTAL).pack()

        tkinter.Button(self, text="OK", command=self.exit_settings).pack()

    def mainloop(self, n: int = ...) -> None:
        while True:
            try:
                self.winfo_exists()
            except tkinter.TclError:
                return
            else:
                sleep(0.05)
                self.control_speed()
                self.display()
                self.update()
        # Please let me know if this code can be improved...


def main():
    core = SortControl(256, 0.002)
    front_end = SortApp(core)
    core.start()
    front_end.mainloop()
    core.exit()
    core.join()


if __name__ == "__main__":
    main()
