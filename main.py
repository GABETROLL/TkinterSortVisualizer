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
from collections.abc import Iterable, Callable


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

        self.sort_classes: dict[str, Algorithm] = {sort_cls.__doc__: sort_cls for sort_cls in sorts}
        self.chosen_sort: Algorithm = BubbleSort(self)
        self.input_classes: dict[str, Algorithm] = {input_cls.__doc__: input_cls for input_cls in inputs}
        self.chosen_input: Algorithm = Linear(self)
        self.shuffle_classes: dict[str, Algorithm] = {shuffle_cls.__doc__: shuffle_cls for shuffle_cls in shuffles}
        self.chosen_shuffle: Algorithm = Shuffle(self)
        self.verify_algorithm = Verify(self)
        # Settings chosen by UI.

        self.chosen_algorithms: Iterable[None] = iter(())
        # chain of all chosen algorithms
        self.reset()
        # define chain

        self.exited = False
        self.playing = False
        # data

    def reset(self):
        """Resets self.chosen_algorithms and resets self as SortPlayground."""
        self.chosen_algorithms = chain(self.chosen_input.run(),
                                       self.chosen_shuffle.run(),
                                       self.chosen_sort.run(),
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

    def choose_input(self, name: str, options: dict[str, object] | None):
        if not (name in self.input_classes):
            raise KeyError(f"Input '{name}' doesn't exist.")
        
        input_cls: Algorithm = self.input_classes[name]
        
        self.chosen_input = (
            input_cls(self, options)
            if options is not None
            else input_cls(self)
        )

        self.stop()
        # restart

    def choose_shuffle(self, name: str, options: dict[str, object] | None):
        if not (name in self.shuffle_classes):
            raise KeyError(f"Shuffle '{name}' doesn't exist.")

        shuffle_cls: Algorithm = self.shuffle_classes[name]

        self.chosen_shuffle = (
            shuffle_cls(self, options)
            if options is not None
            else shuffle_cls(self)
        )

        self.stop()
        # restart

    def choose_sort(self, name: str, options: dict[str, object] | None):
        if not (name in self.sort_classes):
            raise KeyError(f"Sort '{name}' doesn't exist.")

        sort_cls: Algorithm = self.sort_classes[name]

        self.chosen_sort = (
            sort_cls(self, options)
            if options is not None
            else sort_cls(self)
        )

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
        """Returns the num as a frequency in an equal temperament scale
        from `self.lowest` and with `self.octaves` octaves."""
        result = self.lowest * (2 ** self.octaves) ** (num / self.sort_control.main_array_len)
        return result

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


class AlgorithmMenu(tkinter.Frame):
    def __init__(
        self,
        master,
        variable_default: str,
        variable_allowed_values: Iterable,
        variable_name: str,
        update_info: Callable[[str, dict[str, Option]], dict[str, Option]],
    ):
        tkinter.Frame.__init__(self, master)

        self.update_info = update_info

        self.variable = tkinter.StringVar(self, variable_default, variable_name)
        self.option_variables_and_menus: dict[str, (tkinter.Variable, tkinter.Widget)] = {}


        def menu_callback(value: str) -> None:
            default_options: dict[str, Option] = update_info(value, None)
            self.add_options(default_options)


        self.label = tkinter.Label(self, text=variable_name)
        self.menu = tkinter.OptionMenu(
            self,
            self.variable,
            self.variable.get(),
            *variable_allowed_values,
            command=lambda value: menu_callback(value),
        )
        self.menu.pack()
    
    @property
    def options(self) -> dict[str, Option]:
        return {
            name: variable.get()
            for name, (variable, widget) in self.option_variables_and_menus
        }

    def add_options(self, options: dict[str, Option]) -> None:
        for option_name, option_info in options.items():

            option_variable = tkinter.StringVar(self, option_info.value, option_name)

            def callback(value: str) -> None:
                new_options: dict[str, Option] = self.options
                new_options[option_name] = value

                self.update_info(self.variable.get(), new_options)

            option_menu = tkinter.OptionMenu(
                self,
                option_variable,
                option_variable.get(),
                *option_info.allowed_values,
                command=callback
            )
            option_menu.pack()

            self.option_variables_and_menus[option_name] = (
                option_variable,
                option_menu,
            )


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


        def sort_callback(new_sort: str, new_options: dict[str, Option]) -> dict[str, Option]:
            self.sort_control.choose_sort(new_sort, new_options)
            return self.sort_control.chosen_sort.options


        def input_callback(new_input: str, new_options: dict[str, Option]) -> dict[str, Option]:
            self.sort_control.choose_input(new_input, new_options)
            return self.sort_control.chosen_input.options


        def shuffle_callback(new_shuffle: str, new_options: dict[str, Option]) -> dict[str, Option]:
            self.sort_control.choose_shuffle(new_shuffle, new_options)
            return self.sort_control.chosen_shuffle.options


        self.sort_menu = AlgorithmMenu(
            self,
            "Bubble Sort",
            self.sort_control.sort_classes.keys(),
            "sort",
            sort_callback,
        )
        self.input_menu = AlgorithmMenu(
            self,
            "Random Input",
            self.sort_control.input_classes.keys(),
            "input",
            input_callback,
        )
        self.shuffle_menu = AlgorithmMenu(
            self,
            "Nothing",
            self.sort_control.shuffle_classes.keys(),
            "shuffle",
            shuffle_callback,
        )

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

        """sort_name = self.sort_variable.get()
        self.sort_control.choose_sort(
            sort_name,
            self.sort_option_variables
        )

        input_name = self.input_variable.get()
        self.sort_control.choose_input(input_name)

        shuffle_name = self.shuffle_variable.get()
        self.sort_control.choose_shuffle(shuffle_name)

        self.sort_control.change_main_array_len(self.size_variable.get()) """

        self.canvas.pack()
        self.play.pack()
        self.speed_control.pack()
        self.settings_button.pack()

    def goto_settings(self):
        self.clear_screen()

        self.choosing_sort = True

        self.sort_menu.pack()
        self.input_menu.pack()
        self.shuffle_menu.pack()

        tkinter.Scale(self, from_=1, to=1024, variable=self.size_variable, length=1024, orient=tkinter.HORIZONTAL).pack()

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
