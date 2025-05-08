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


def rainbow_color(num: int, max_num: int) -> str:
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
        # To refresh coroutines when they amount.

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
    """
    OutputStream of frequencies representing nums in SortControl.

    `self.sort_control` contains all the information about the sorts currently being played,
    including what numbers in the array are currently being read/written. These are kept track of
    in `self.sort_control.pointers`.

    The point of this class is to create an instance of it, that for each frame it's called,
    for each number pointed to in `self.sort_control`, plays a note
    that represents the number being pointed to, with the pitch indicating the scale of the number.

    Each time `callback` is called,
    it returns a new numpy.array that represents the audio that needs to be played for this frame.

    `octaves`: The amount of octaves of range the notes representing the numbers have.
    """
    def __init__(self, sort_control: SortControl, octaves: int):
        self.lowest = 210
        sounddevice.OutputStream.__init__(self, blocksize=self.lowest, channels=1, callback=self.callback)
        # 210 divides 44100 evenly.
        # Should also match the harmonics of the lowest note.
        # (??)

        self.sort_control = sort_control

        self.octaves: int = octaves
        """
        The amount of octaves of range the notes representing the numbers have.
        """

        self.frequencies: dict[float, int] = {}
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
        return self.minimum_duration

    def frequency(self, num: int) -> float:
        """Returns the num as a frequency in an equal temperament scale
        from `self.lowest` and with `self.octaves` octaves."""
        result = self.lowest * (2 ** self.octaves) ** (num / self.sort_control.main_array_len)
        return result

    def store_new_frequencies(self) -> None:
        """
        Keeps track of each new frequency to play,
        based on the numbers in `self.sort_control.read_at_pointers`.

        Looks at each num pointed to in `self.sort_control.read_at_pointers`,
        and if the frequency isn't already in `self.frequencies`, it adds the frequency
        with an index of 0. Otherwise, it leaves its index the same.
        """
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
        """
        Returns the added sine waves of all nums
        currently pointed at by self.sort_control, FOR THIS BLOCK OF AUDIO.

        The individual sine waves of each num are added together,
        by adding each of their graphs at each corresponding point in the current block.

        This block should be `frames` units long.
        
        Each frequency added by `self.store_new_frequencies` in `self.frequencies`
        starts with a corresponding index of 0. These indices exist to keep track of
        "where in the sine wave graph" the frequency was left from the last audio block.
        Then, every time this function is called,
        the frequency's index is incremented by `frames` (Each "frame"
        is a point in the result graph, and represents 1/frames of this audioblock).
        """
        result: numpy.ndarray = numpy.zeros((frames,))

        for frequency, start_index in self.frequencies.copy().items():
            stop_index: int = start_index + frames
            """
            (EXCLUSIVE)
            """

            range_of_indices: numpy.ndarray = numpy.arange(start_index, stop_index, 1)
            x_coordinates_of_sin_x: numpy.ndarray = range_of_indices * 2 * numpy.pi * frequency / self.samplerate
            frequency_graph: numpy.ndarray = numpy.sin(x_coordinates_of_sin_x)

            block_amplitudes: numpy.ndarray = numpy.clip((self.duration - range_of_indices) / self.duration, 0, 1)
            """
            The amplitude of the frequency at each frame.
            Should decrease linearly from 1 to 0.

            The amplitudes should clamp at 0.
            """

            note_audio: numpy.ndarray = frequency_graph * block_amplitudes

            # these both have shape (frames,)
            assert result.shape == note_audio.shape, (result.shape, note_audio.shape)

            result += note_audio

            if (stop_index > self.duration):
                self.frequencies.pop(frequency)
            else:
                self.frequencies[frequency] += frames

        return result

    def callback(self, outdata: numpy.ndarray, frames: int, time, status) -> None:
        """writes sound output to 'outdata' Called by self in sounddevice.OutputStream."""
        # params may need annotations... :/
        self.store_new_frequencies()
        result: numpy.ndarray = self.sine_waves(frames).reshape((frames,1))
        outdata[:] = result


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

        # The goal here is to decide what the max number's height in the canvas will be,
        # so that the rest of the numbers's heights are drawn in proportion to the max number.
        #
        # I want to display all arrays taking up equal space in the height of the canvas,
        # with the main array at the bottom, and each new array higher and higher.
        # Therefore, the max height of a number in any array (`max_height`) is
        # the height of the canvas divided by the amount of arrays.
        bar_width = self.canvas.winfo_width() / (self.sort_control.main_array_len + 1)
        max_height = self.canvas.winfo_height() / self.sort_control.array_count

        for array_index, array in enumerate(self.sort_control.arrays):

            for num_index, num in enumerate(array):
                # Setting the height of the current number such that
                # its ratio with the height of the array in the canvas
                # equals the ratio of the number to the max number of the array.
                #
                # The array's length cannot be 0, but in case it somehow is,
                # to prevent dividing by 0, set the height of that array in the canvas to 0,
                # as if the array weren't even there.
                try:
                    height = max_height * num / self.sort_control.main_array_len
                    # Since the max number in the main array SHOULD BE
                    # no greater than the length of the main array,
                    #
                    # Just assume that the max number in the array IS EQUAL TO the array's len.
                except ZeroDivisionError:
                    height = 0

                x0 = num_index * bar_width
                x1 = x0 + bar_width

                y0 = self.canvas.winfo_height() - max_height * array_index
                y1 = y0 - height

                color = "black" if (array_index, num_index) in self.sort_control.pointers else \
                    rainbow_color(num, self.sort_control.main_array_len)

                self.canvas.create_rectangle(x0,
                                             y0,
                                             x1,
                                             y1,
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
