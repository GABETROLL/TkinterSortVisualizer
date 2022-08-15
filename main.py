import tkinter
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


class SortApp(tkinter.Tk, SortPlayground):
    """Container for all sorts, settings and shuffles.
    Runs loop with algorithm coroutines during the main window mainloop.
    Controls playing and pausing."""

    def __init__(self, capacity: int, delay: float):
        SortPlayground.__init__(self, capacity, delay)
        tkinter.Tk.__init__(self)

        self.canvas = tkinter.Canvas(self, width=1024, height=512)
        self.canvas.pack()

        self.play = tkinter.Button(self, text="play", command=self.pause_play)
        self.play.pack()
        # buttons

        self.sorts = [HeapSort(self), RadixSort(self), MergeSort(self), BubbleSort(self), SelectionSort(self), InsertionSort(self)]
        self.sort = iter(())

        self.shuffles = [AlreadySorted(self), Reversed(self), Shuffle(self)]
        self.shuffle = iter(())

        self.verify_algorithm = Verify(self)
        self.verify = iter(())

        self.reset()

        self.playing = False
        # data

    def display(self):
        self.canvas.delete("all")

        bar_width = self.canvas.winfo_width() / (self.capacity + 1)
        max_height = self.canvas.winfo_height() / len(self.arrays)

        for array_index, array in enumerate(self.arrays):

            biggest = max(array)

            for num_index, num in enumerate(array):
                try:
                    height = max_height * num / biggest
                except ZeroDivisionError:
                    height = 0

                x0 = num_index * bar_width
                x1 = x0 + bar_width

                y0 = max_height * array_index

                color = "black" if (array_index, num_index) in self.pointers else rainbow_color(num, biggest)

                self.canvas.create_rectangle(x0,
                                             y0,
                                             x1,
                                             y0 + height,
                                             fill=color)
        self.canvas.update()

    def reset(self):
        """Resets self playground and coroutines."""
        SortPlayground.reset(self)

        self.sort = self.sorts[0].run()
        self.shuffle = self.shuffles[0].run()
        self.verify = self.verify_algorithm.run()

    def stop(self):
        self.playing = False
        self.reset()
        self.play.config(text="play")

    def pause_play(self):
        self.playing = not self.playing
        self.play.config(text="pause" if self.playing else "play")

    def run(self):
        while True:
            algorithms = chain(self.shuffle, self.sort, self.verify)

            if self.playing:
                try:
                    next(algorithms)
                except StopIteration:
                    self.stop()

                    continue
                else:
                    try:
                        self.display()
                    except tkinter.TclError:
                        break

            try:
                self.winfo_exists()
            except tkinter.TclError:
                break

            self.update()


def main():
    root = SortApp(512, 0)
    root.run()


if __name__ == "__main__":
    main()
