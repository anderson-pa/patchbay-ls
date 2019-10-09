"""
    Modified from:
        Python Example stepper motor driver
        Author:  D Mecer
        Revision: 11/27/2013
"""

import time
import dwf
from tkinter import *

master = Tk()
step_time = 0.001
hdwf = dwf.Dwf()
digo = dwf.DwfDigitalOut(hdwf)
digio = dwf.DwfDigitalIO(hdwf)

print(f'DWF Version: {dwf.FDwfGetVersion()}')


# generate on D0 - D3 50 Hz pulse (100MHz/500000/(3+1)), 25% duty (3low 1high)
for ch in range(4):
    digo.enableSet(ch, True)
    digo.dividerSet(ch, 500000)
    digo.counterSet(ch, 3, 1)

digio.outputEnableSet(0x00F0)
digio.outputSet(0x00F0)


def step_forward():
    digo.configure(0)
    time.sleep(0.1)
    step_count = eval(e1.get())
    print("Number of forward steps requested " + str(step_count))

    # initialize counters for four phases
    for ch in range(4):
        digo.counterInitSet(ch, 1, ch + 1)

    run_time = (step_count + 0.7) / 100.0
    print("Run time for forward steps " + str(run_time))
    digo.runSet(run_time)
    digo.repeatSet(1)
    digo.configure(1)


def step_reverse():
    digo.configure(0)
    time.sleep(0.1)
    step_count = eval(e1.get())
    print("Number of reverse steps requested " + str(step_count))

    # initialize counters for four phases
    for ch in range(4):
        digo.counterInitSet(ch, 1, 4 - ch)

    run_time = (step_count + 0.7) / 100.0
    print("Run time for reverse steps " + str(run_time))
    digo.runSet(run_time)
    digo.repeatSet(1)
    digo.configure(1)


# forward rotation routine
def step_2_forward():
    # digo.configure(0)
    # time.sleep(0.1)
    # step_count = eval(e1.get())
    # print("Number of forward steps requested " + str(step_count))
    #
    # # initialize counters for four phases
    # for ch in range(4):
    #     digo.counterInitSet(ch + 4, 1, 1)
    #
    # run_time = (step_count + 0.7) / 100.0
    # print("Run time for forward steps " + str(run_time))
    # digo.runSet(run_time)
    # digo.repeatSet(1)
    # digo.configure(1)

    step_count = eval(e1.get())
    step_time = eval(e2.get())
    print("Number of forward steps requested " + str(eval(e1.get())))
    i = 0
    while i < step_count:
        digio.outputSet(0x10)
        time.sleep(step_time)
        digio.outputSet(0x30)
        time.sleep(step_time)

        digio.outputSet(0x20)
        time.sleep(step_time)
        digio.outputSet(0x60)
        time.sleep(step_time)

        digio.outputSet(0x40)
        time.sleep(step_time)
        digio.outputSet(0xC0)
        time.sleep(step_time)

        digio.outputSet(0x80)
        time.sleep(step_time)
        digio.outputSet(0x90)
        time.sleep(step_time)


        i = i + 1
    # turns off all bits while idle
    digio.outputSet(0x00)


# reverse rotation routine
def step_2_reverse():
    step_count = eval(e1.get())
    step_time = eval(e2.get())
    print("Number of forward steps requested " + str(eval(e1.get())))
    i = 0
    while i < step_count:
        digio.outputSet(0x0080)
        time.sleep(step_time)
        digio.outputSet(0x0040)
        time.sleep(step_time)
        digio.outputSet(0x0020)
        time.sleep(step_time)
        digio.outputSet(0x0010)
        time.sleep(step_time)

        i = i + 1
    # turns off all bits while idle
    # digio.outputSet(0x00)


def close_handle():
    digo.close()
    master.quit()

# Build GUI
l1 = Label(master, text="Number of Steps")
l1.grid(row=0, sticky=W)
e1 = Entry(master)
e1.grid(row=1, sticky=W, pady=4)
e1.delete(0, "end")
e1.insert(0, 5)

l2 = Label(master, text="Step Time")
l2.grid(row=2, sticky=W)
e2 = Entry(master)
e2.grid(row=3, sticky=W, pady=4)
e2.delete(0, "end")
e2.insert(0, 0.1)
#
b1 = Button(master, text='Forward', command=step_forward)
b1.grid(row=4, sticky=W, pady=4)
b2 = Button(master, text='Reverse', command=step_reverse)
b2.grid(row=5, sticky=W, pady=4)
b3 = Button(master, text='Forward2', command=step_2_forward)
b3.grid(row=4, sticky=E, pady=4)
b4 = Button(master, text='Reverse2', command=step_2_reverse)
b4.grid(row=5, sticky=E, pady=4)

b5 = Button(master, text='Quit', command=close_handle)
b5.grid(row=6, sticky=W, pady=4)
mainloop()

# ====================

# Build GUI
# l1 = Label(master, text="Number of Steps")
# l1.grid(row=0, sticky=W)
# e1 = Entry(master)
# e1.grid(row=1, sticky=W, pady=4)
# e1.delete(0, "end")
# e1.insert(0, 10)
# l2 = Label(master, text="Step Time")
# l2.grid(row=2, sticky=W)
# e2 = Entry(master)
# e2.grid(row=3, sticky=W, pady=4)
# e2.delete(0, "end")
# e2.insert(0, 0.001)
# #
# b1 = Button(master, text='Forward', command=BForward)
# b1.grid(row=4, sticky=W, pady=4)
# b2 = Button(master, text='Reverse', command=BReverse)
# b2.grid(row=5, sticky=W, pady=4)
#
# b3 = Button(master, text='Quit', command=BCloseDev)
# b3.grid(row=6, sticky=W, pady=4)
# mainloop()



