from __future__ import division
try:
    from tkinter import *
    from tkinter.colorchooser import askcolor
    import six.moves.tkinter as tk
except ImportError:
    from Tkinter import *
    from tkColorChooser import askcolor
import time
import numpy
import pyopencl
import traceback
import logging
import os
from PIL import Image, ImageTk
from functools import partial
from six.moves import range

iteration = 50
context = None
firsttime = 0
zoomscale = 1
is64bit = 0
width = 900#1915
height = 900#950


class Fractal():
    def __init__(self):
        self.root = Tk()
        self.root.title("Fractal viewer")
        self.bgcolour = [255, 255, 255]
        self.pos = [-2, 2, -2, 2]#[-2.5, 1.1, -1.3, 1.3]
        self.render(255, 0, 0)
        self.fillGUI()

        self.root.mainloop()


    def getColour(self):
        colour = askcolor()

        self.bgcolour[0] = colour[0][0]
        self.bgcolour[1] = colour[0][1]
        self.bgcolour[2] = colour[0][2]
        self.rerender()


    def move(self, direction):
        try:
            difX = self.pos[1] - self.pos[0]
            difY = self.pos[3] - self.pos[2]
            
            global zoomscale
            
            if direction == "left" or direction == "a":
                self.pos[0] -= abs(difX/4)
                self.pos[1] -= abs(difX/4)
            elif direction == "right" or direction == "d":
                self.pos[0] += abs(difX/4)
                self.pos[1] += abs(difX/4)
            elif direction == "up" or direction == "w":
                self.pos[2] += abs(difY/4)
                self.pos[3] += abs(difY/4)
            elif direction == "down" or direction == "s":
                self.pos[2] -= abs(difY/4)
                self.pos[3] -= abs(difY/4)
            elif direction == "in":
                self.pos[0] += abs(difX/6)
                self.pos[1] -= abs(difX/6)
                self.pos[2] += abs(difY/6)
                self.pos[3] -= abs(difY/6)
            elif direction == "out":
                self.pos[0] -= abs(difX/6)
                self.pos[1] += abs(difX/6)
                self.pos[2] -= abs(difY/6)
                self.pos[3] += abs(difY/6)

                #print("Left: ", self.pos[0], " Right: ", self.pos[1], " Top: ", self.pos[2], " Bottom: ", self.pos[3])
                zoomscale = zoomscale * 1.045                   
            
            self.rerender()

        except Exception as e:
            logging.error(traceback.format_exc())


    def generateFractal(self, left, right, bottom, top, iterations=iteration, fractalType=0):
        xArray = numpy.arange(left, right, (right-left)/width)
        yArray = numpy.arange(top, bottom, (bottom-top)/height) * 1j

        while len(xArray) > width:
            xArray = numpy.delete(xArray, len(xArray)-1, 0)
        while len(yArray) > height:
            yArray = numpy.delete(yArray, len(yArray)-1, 0)

        if is64bit == 0:
            tempArray = numpy.ravel(xArray+yArray[:, numpy.newaxis]).astype(numpy.complex64)
        else:
            tempArray = numpy.ravel(xArray+yArray[:, numpy.newaxis]).astype(numpy.complex128)

        matrix = calculate(tempArray, iterations, fractalType)
        self.fractal = (matrix.reshape(height, width) / float(matrix.max()) * 255).astype(numpy.uint8)


    
    def getMousePos(self, event):
        global width, height
        xcoord = event.x
        ycoord = event.y
        
        diffX = self.pos[1] - self.pos[0]
        cplxX = self.pos[0] + ((diffX / width) * xcoord)#convert pos to cplx coord
        diffY = self.pos[2] - self.pos[3]
        cplxY = self.pos[3] + ((diffY / height) * ycoord)

        if event.num == 1:
            self.mouseMove(cplxX, cplxY, "in")
        else:
            self.mouseMove(cplxX, cplxY, "out")


    def mouseMove(self, x, y, direction):
        tempWidth = self.pos[1] - self.pos[0]
        tempHeight = self.pos[2] - self.pos[3]

        self.pos[0] = x - (0.5 * tempWidth)
        self.pos[1] = x + (0.5 * tempWidth)
        self.pos[2] = y + (0.5 * tempHeight)
        self.pos[3] = y - (0.5 * tempHeight)

        self.move(direction)

    def wasdMove(self, event):
        self.move(event.char)

    def enable64bit(self):
        global is64bit
        if is64bit == 0:
            is64bit = 1
        else:
            is64bit = 0

        self.rerender()


    def render(self, r, g, b):
        self.generateFractal(self.pos[0], self.pos[1], self.pos[2], self.pos[3])
        self.colouredImage = Image.fromarray(self.fractal)
        self.colouredImage.putpalette([i for rgb in ((int(round(j/(255/(self.bgcolour[0]+1)))), int(round(j/(255/(self.bgcolour[1]+1)))), int(round(j/(255/(self.bgcolour[2]+1))))) for j in range(255))
                            for i in rgb])

    def rerender(self, value=0):
        self.generateFractal(self.pos[0], self.pos[1], self.pos[2], self.pos[3], self.iterationSlider.get(), self.fractalSelector.curselection())
        self.colouredImage = Image.fromarray(self.fractal)
        self.colouredImage.putpalette([i for rgb in ((int(round(j/(255/(self.bgcolour[0]+1)))), int(round(j/(255/(self.bgcolour[1]+1)))), int(round(j/(255/(self.bgcolour[2]+1))))) for j in range(255))
                            for i in rgb])
        self.image = ImageTk.PhotoImage(self.colouredImage)
        self.label.configure(image = self.image)

    def fillGUI(self):
        global is64bit
        self.colourButton = Button(text='Choose background colour', command=self.getColour)
        self.colourButton.grid(row=0, sticky=W)
        self.iterationSlider = Scale(from_=0, to=1000, orient=HORIZONTAL, label='Iterations', length=220, command=self.rerender)
        self.iterationSlider.set(iteration)
        self.iterationSlider.grid(row=0, column=1, sticky=W)
        self.leftButton = Button(text='Left', command=lambda: self.move("left"))
        self.leftButton.grid(row=0, column=2, sticky=W)
        self.rightButton = Button(text='Right', command=lambda: self.move("right"))
        self.rightButton.grid(row=0, column=3, sticky=W)
        self.upButton = Button(text='Up', command=lambda: self.move("up"))
        self.upButton.grid(row=0, column=4, sticky=W)
        self.downButton = Button(text='Down', command=lambda: self.move("down"))
        self.downButton.grid(row=0, column=5, sticky=W)
        self.zoomInButton = Button(text='Zoom in', command=lambda: self.move("in"))
        self.zoomInButton.grid(row=0, column=6, sticky=W)
        self.zoomOutButton = Button(text='Zoom out', command=lambda: self.move("out"))
        self.zoomOutButton.grid(row=0, column=7, sticky=W)
        self.is64bitBox = Checkbutton(text='64 bit', variable=is64bit, command=self.enable64bit)
        self.is64bitBox.grid(row=0, column=8, sticky=W)
        self.fractalSelector = Listbox(height=5)
        self.fractalSelector.grid(row=0, column=9, sticky=W)
        self.fractalSelector.bind("<Double-Button-1>", self.rerender)
        for i in ["Mandelbrot", "Julia"]:
            self.fractalSelector.insert(END, i)

        self.image = ImageTk.PhotoImage(self.colouredImage)
        self.label = Label(self.root, image=self.image)
        self.label.grid(row=1, columnspan=10)
        self.label.bind("<Button-1>", self.getMousePos)
        self.label.bind("<Button-3>", self.getMousePos)
        
        self.root.bind("w", self.wasdMove)
        self.root.bind("a", self.wasdMove)
        self.root.bind("s", self.wasdMove)
        self.root.bind("d", self.wasdMove)


def fractalOpenCL(tempArray, iterations, fractalType):
    global firsttime, context
    if firsttime == 0:
        context = pyopencl.create_some_context()
        firsttime += 1

    commandQueue = pyopencl.CommandQueue(context)
    matrix = numpy.empty(tempArray.shape, dtype=numpy.uint16)
    OpenCLBuffer1 = pyopencl.Buffer(context, pyopencl.mem_flags.READ_ONLY | pyopencl.mem_flags.COPY_HOST_PTR, hostbuf=tempArray)
    OpenCLBuffer2 = pyopencl.Buffer(context, pyopencl.mem_flags.WRITE_ONLY, matrix.nbytes)

    if str(fractalType) != "(1,)": #if Mandelbrot
        if is64bit == 0:
            type1 = "float2"
            type2 = "float"
            type3 = "f"
        else:
            type1 = "double2"
            type2 = "double"
            type3 = ""

        code = open(os.path.dirname(os.path.realpath(__file__)) + '\mandelbrot.cl', 'r')
        read = "".join(code.readlines())
        formattedRead = read.format(type1, type2, type3)
        fractal = pyopencl.Program(context, formattedRead).build()
        fractal.mandelbrot(commandQueue, matrix.shape, None, OpenCLBuffer1, OpenCLBuffer2, numpy.uint16(iterations))
        
    else: #if Julia
        if is64bit == 0:
            type1 = "float2"
            type2 = "float"
            type3 = "f"
        else:
            type1 = "double2"
            type2 = "double"
            type3 = ""

        code = open(os.path.dirname(os.path.realpath(__file__)) + '\julia.cl', 'r')
        read = "".join(code.readlines())
        formattedRead = read.format(type1, type2, type3)
        fractal = pyopencl.Program(context, formattedRead).build()
        fractal.julia(commandQueue, matrix.shape, None, OpenCLBuffer1, OpenCLBuffer2, numpy.uint16(iterations))

    pyopencl.enqueue_copy(commandQueue, matrix, OpenCLBuffer2).wait()

    return matrix


def fractalPython(c, iterations, fractalType):
    if str(fractalType) != "(1,)": #if Mandelbrot
        if is64bit == 0:
            z = numpy.zeros(c.shape, numpy.complex64)
        else:
            z = numpy.zeros(c.shape, numpy.complex128)
        matrix = numpy.resize(numpy.array(0), c.shape)
        for i in range(len(c)):
            for iter in range(iterations):
                z[i] = z[i]*z[i] + c[i]
                if abs(z[i]) > 2.0:
                    matrix[i] = iter
                    break
    else: #if Julia
        if is64bit == 0:
            z = numpy.zeros(c.shape, numpy.complex64)
        else:
            z = numpy.zeros(c.shape, numpy.complex128)
        for i in range(len(c)):
            z[i] = c[i]
        matrix = numpy.resize(numpy.array(0), c.shape)
        for i in range(len(c)):
            for iter in range(iterations):
                z[i] = z[i]*z[i] + complex(0.285, 0.01)
                if abs(z[i]) > 2.0:
                    matrix[i] = iter
                    break
    return matrix


mode = input("How would you like to calculate the fractal? Choose 1 to use Python's built-in maths libraries, or 2 for OpenCL (where applicable). ")
if mode == 1:
    calculate = fractalPython
else:
    calculate = fractalOpenCL


start = Fractal()

