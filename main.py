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


# sort: Bubble Sort
#       Radix Sort
#         base: 2
#               ...
#               1024
#
# MenuData(
#   "sort",
#   "Bubble Sort",
#   {
#     "Bubble Sort": []
#     "Radix Sort": [
#       MenuData(
#         "base",
#         2,
#         {
#           2: [],
#           ...
#           1024: [],
#         },
#       ),
#     ],
#   },
# )
@dataclass
class MenuData:
    name: str
    initial_value: object
    allowed_values: Iterable
    value_sub_menus: dict[object, list]


# v = tkinter.Variable(self, "Bubble Sort", "sort")
# m = tkinter.OptionMenu(self, v, v.get(), *menu_data.allowed_values.keys())
#   vr = tkinter.Variable(self, 2, base)
#   mr = tkinter.OptionMenu(self, vr, vr.get(), *)

class AlgorithmMenu:
    def __init__(
        self,
        master,
        menu_data: MenuData,
        update_info: Callable[[str, dict[str, Option]], None],
    ):
        self.update_info = update_info

        self.menu_data: MenuData = menu_data

        self.variable = tkinter.Variable(master, menu_data.initial_value, menu_data.name)
        self.label = tkinter.Label(master, text=menu_data.name)

        # print(type(menu_data.allowed_values))

        if isinstance(menu_data.allowed_values, range):
            self.menu = tkinter.Scale(
                master,
                variable=self.variable,
                from_=menu_data.allowed_values.start,
                to=menu_data.allowed_values.stop - 1,
                orient="horizontal",
                length=len(menu_data.allowed_values),
                command=lambda value: self.menu_callback(int(value)),
            )
        else:
            self.menu = tkinter.OptionMenu(
                master,
                self.variable,
                self.variable.get(),
                *menu_data.allowed_values,
                command=self.menu_callback,
            )

        self.sub_menus: dict[object, list[AlgorithmMenu]] = {}
        """
        A dictionary of all the options for this menu,
        and all of the sub-menus that need to spawn on screen
        when each corresponding option was chosen.
        """


        def child_update_info(child_name: str, child_options: dict[str, Option]):
            # print(f"CHILD UPDATING: {child_name = }, {child_options = }")

            new_sub_options: dict[str, Option] = self.current_sub_options
            new_sub_options[child_name] = child_options

            update_info(self.variable.get(), new_sub_options)


        for option, option_menu_datas in menu_data.value_sub_menus.items():
            option_algorithm_menus: list[AlgorithmMenu] = []

            for option_menu_data in option_menu_datas:
                option_algorithm_menus.append(
                    AlgorithmMenu(master, option_menu_data, child_update_info)
                )

            self.sub_menus[option] = option_algorithm_menus

        # print(self.sub_menus)

    def __repr__(self) -> str:
        return f"AlgorithmMenu(name={self.menu_data.name}, value={self.variable.get()}, sub_menus={ {option: repr(menu_list) for option, menu_list in self.sub_menus.items()} })"

    @property
    def current_sub_options(self) -> dict[str, Option]:
        """
        The state of the currently chosen options (in the tkinter menus)
        in the children `AlgorithmMenu`'s that SHOULD be spawned when `self`'s
        current option is selected.

        This property DOES NOT return the sub-options of those sub-menus, recursively.
        """
        child_nodes: list[AlgorithmMenu] = self.sub_menus[self.variable.get()]

        return {
            child_node.menu_data.name: Option(child_node.variable.get(), child_node.menu_data.allowed_values)
            for child_node in child_nodes
        }
    
    def pack(self) -> None:
        self.label.pack()
        self.menu.pack()

        current_option_sub_menus: list[AlgorithmMenu] = self.sub_menus[self.variable.get()]
        for sub_menu in current_option_sub_menus:
            sub_menu.pack()

    def pack_forget(self) -> None:
        current_option_sub_menus: list[AlgorithmMenu] = self.sub_menus[self.variable.get()]
        for sub_menu in current_option_sub_menus:
            sub_menu.pack_forget()

        self.label.pack_forget()
        self.menu.pack_forget()

    def menu_callback(self, value: object) -> None:
        """
        The callback for `self.menu`, so that when the user chooses `value`
        through `self.menu`, this method calls `self.update_info` with
        the chosen value and all of the options from the value's corresponding sub-menus.

        This method also un-packs all child menus from `self`
        (in `self.sub_menus[*][*]`), and packs `value`'s
        corresponding sub-menus into `self`
        (packs `self.sub_menus[value][*]`).
        """
        self.update_info(value, self.current_sub_options)

        for option_menu_list in self.sub_menus.values():
            for menu in option_menu_list:
                menu.pack_forget()

        for menu in self.sub_menus[value]:
            menu.pack()


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


        def generate_menu(
            master: tkinter.Widget,
            menu_name: str,
            chosen_algorithm_name: str,
            algorithm_classes_dict: dict[str, Algorithm],
            menu_callback: Callable[[str, dict[str, Option]], None],
        ) -> AlgorithmMenu:
            return AlgorithmMenu(
                master,
                MenuData(
                    menu_name,
                    chosen_algorithm_name,
                    algorithm_classes_dict.keys(),
                    {
                        name: [
                            MenuData(
                                option_name,
                                option_info.value,
                                option_info.allowed_values,
                                {value: [] for value in option_info.allowed_values},
                            )
                            for option_name, option_info in algorithm.options.items()
                        ]
                        for name, algorithm in {
                            name: algorithm_cls(self.sort_control)
                            for name, algorithm_cls in algorithm_classes_dict.items()
                        }.items()
                    },
                ),
                menu_callback,
            )


        def sort_callback(new_sort: str, new_options: dict[str, Option]) -> None:
            self.sort_control.choose_sort(new_sort, new_options)


        def input_callback(new_input: str, new_options: dict[str, Option]) -> None:
            self.sort_control.choose_input(new_input, new_options)


        def shuffle_callback(new_shuffle: str, new_options: dict[str, Option]) -> None:
            self.sort_control.choose_shuffle(new_shuffle, new_options)


        self.sort_menu_frame = tkinter.Frame(self)
        self.sort_menu: AlgorithmMenu = generate_menu(
            self.sort_menu_frame,
            "sort",
            self.sort_control.chosen_sort.__doc__,
            self.sort_control.sort_classes,
            sort_callback,
        )
        self.sort_menu.pack()
        self.input_menu_frame = tkinter.Frame(self)
        self.input_menu: AlgorithmMenu = generate_menu(
            self.input_menu_frame,
            "input",
            self.sort_control.chosen_input.__doc__,
            self.sort_control.input_classes,
            input_callback,
        )
        self.input_menu.pack()
        self.shuffle_menu_frame = tkinter.Frame(self)
        self.shuffle_menu: AlgorithmMenu = generate_menu(
            self.shuffle_menu_frame,
            "shuffle",
            self.sort_control.chosen_shuffle.__doc__,
            self.sort_control.shuffle_classes,
            shuffle_callback,
        )
        self.shuffle_menu.pack()

        self.size_variable = tkinter.IntVar(self, self.sort_control.main_array_len)
        self.choosing_sort = False

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

        self.sort_control.change_main_array_len(self.size_variable.get())

        self.canvas.pack()
        self.play.pack()
        self.speed_control.pack()
        self.settings_button.pack()

    def goto_settings(self):
        self.clear_screen()

        self.choosing_sort = True

        self.sort_menu_frame.pack(fill=tkinter.X)
        self.input_menu_frame.pack(fill=tkinter.X)
        self.shuffle_menu_frame.pack(fill=tkinter.X)

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
