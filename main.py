import tkinter
from threading import Thread
from time import sleep
from sorting import *
from itertools import chain
from colorsys import hsv_to_rgb


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

    def __init__(self, capacity: int, delay: float):
        Thread.__init__(self)
        SortPlayground.__init__(self, capacity)

        self.delay = delay

        self.sorts = [sort(self) for sort in sorts]
        self.sort = iter(())

        self.shuffles = [shuffle(self) for shuffle in shuffles]
        self.shuffle = iter(())

        self.verify_algorithm = Verify(self)
        self.verify = iter(())

        self.reset()

        self.exited = False
        self.playing = False
        # data

    def reset(self):
        """Resets self playground and coroutines."""
        SortPlayground.reset(self)

        self.sort = self.sorts[0].run()
        self.shuffle = self.shuffles[0].run()
        self.verify = self.verify_algorithm.run()

    def stop(self):
        self.playing = False
        self.reset()

    def pause_play(self):
        self.playing = not self.playing

    def exit(self):
        self.exited = True

    def run(self):
        while not self.exited:
            algorithms = chain(self.shuffle, self.sort, self.verify)

            if self.playing:
                try:
                    next(algorithms)
                except StopIteration:
                    self.stop()
            sleep(self.delay)


class SortApp(tkinter.Tk):
    def __init__(self, sort_control: SortControl):
        tkinter.Tk.__init__(self)

        self.sort_control = sort_control

        self.canvas = tkinter.Canvas(self, width=1024, height=512)
        self.canvas.pack()

        self.play = tkinter.Button(self, text="play", command=self.sort_control.pause_play)
        self.play.pack()

    def display(self):
        self.canvas.delete("all")

        bar_width = self.canvas.winfo_width() / (self.sort_control.capacity + 1)
        max_height = self.canvas.winfo_height() / self.sort_control.array_count

        for array_index, array in enumerate(self.sort_control.arrays):

            biggest = max(array)

            for num_index, num in enumerate(array):
                try:
                    height = max_height * num / biggest
                except ZeroDivisionError:
                    height = 0

                x0 = num_index * bar_width
                x1 = x0 + bar_width

                y0 = max_height * array_index

                color = "black" if (array_index, num_index) in self.sort_control.pointers else rainbow_color(num, biggest)

                self.canvas.create_rectangle(x0,
                                             y0,
                                             x1,
                                             y0 + height,
                                             fill=color,
                                             outline=color)
        self.canvas.update()

    def mainloop(self, n: int = ...) -> None:
        while True:
            try:
                self.winfo_exists()
            except tkinter.TclError:
                return
            else:
                self.display()
                self.update()
        # Please let me know if this code can be improved...


def main():
    core = SortControl(512, 0.0001)
    front_end = SortApp(core)
    core.start()
    front_end.mainloop()
    core.exit()
    core.join()


if __name__ == "__main__":
    main()
