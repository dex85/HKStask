# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

author: Alexander Keller

description: calibration demo
"""
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

# make plot global for the update function
figure = plt.Figure(figsize = (8, 2.8), dpi = 100)
figure.subplots_adjust(top = 0.9, bottom = 0.1, left = 0.1, right = 0.9, hspace=0., wspace = 0.)
ax = figure.add_subplot(111)


class WeldScannerCalibration:
    def __init__(self, currents = [50, 100, 150, 200, 250], intervalMs = 500):
        self.currents = currents
        self.updateIntervalMs = intervalMs
        self.voltages = []
        self.xlabels = []
        self.state = 0
        self.iStates = []
        self.currentIds = []
        self.stateColor = 'red'
        self.historyVoltages = []
        self.historyColors = []
        
        #############################################################
        ####                                                    #####
        ####    Create the Layout                               #####
        ####                                                    #####
        #############################################################    
        bgColor = "#add8e6"

        # for changing the current
        self.slider = Tk()
        self.slider.geometry("50x300")

        self.scaler = Scale(self.slider,
                   label = "  A",
                   from_ = 0,
                   to = 300,
                   resolution = 10,
                   tickinterval = 50,
                   #command = getSliderValues,
                   length = 300,
                   cursor = 'hand1',
                   orient = VERTICAL)
        self.scaler.pack()

        # the main window
        self.root = Tk()
        self.root.geometry("800x520")
        self.root.configure(background = "white")

        # heading and measuring points
        self.headFrame = Frame(self.root, width = 800, height = 30, bg = bgColor)
        self.headingLabel = Label(self.headFrame, text = "Messpkunkt 1", bg = bgColor, font = ("Helvetica", 32, "bold"))
        self.headingLabel.pack(side = TOP)

        self.valuesFrame = Frame(self.headFrame, width = 800, bg = bgColor)
        self.valuesFrame.pack(side = TOP)

        self.headFrame.pack(side = TOP)

        # the chart for visualization of the measurement
        self.chartFrame = Frame(self.root, width = 800, bg = bgColor)
        self.chartFrame.pack(side = TOP)

        # the footer with actual and target values and control buttons
        self.bottomFrame = Frame(self.root, width = 750, bg = "white")
        self.bottomFrame.pack(side = TOP, pady = 5)

        self.bottomFrameLeft = LabelFrame(self.bottomFrame, text = "Spannung - Ist\t\tSoll", bg = bgColor, font = ("Helvetica", 12, "bold"))
        self.bottomFrameMiddle = Label(self.bottomFrame, text = "", width = 8, bg = "white", font = ("Helvetica", 12, "bold"))
        self.bottomFrameRight = LabelFrame(self.bottomFrame, text = "Strom - Ist\t\tSoll", bg = bgColor, font = ("Helvetica", 12, "bold"))
        self.bottomFrameLeft.pack(side = LEFT)
        self.bottomFrameMiddle.pack(side = LEFT)
        self.bottomFrameRight.pack(side = RIGHT)

        self.voltageActualLabel = Label(self.bottomFrameLeft, width = 6, text = "", font = ("Helvetica", 30, "bold"))
        self.voltageTargetLabel = Label(self.bottomFrameLeft, width = 6, text = "", font = ("Helvetica", 30, "bold"))
        self.voltageActualLabel.pack(padx = 5, pady = 5, side = LEFT)
        self.voltageTargetLabel.pack(padx = 5, pady = 5, side = LEFT)

        self.currentActualLabel = Label(self.bottomFrameRight, width = 6, text = "", font = ("Helvetica", 30, "bold"), )
        self.currentTargetLabel = Label(self.bottomFrameRight, width = 6, text = "", font = ("Helvetica", 30, "bold"))
        self.currentTargetLabel.pack(padx = 5, pady = 5, side = RIGHT)
        self.currentActualLabel.pack(padx = 5, pady = 5, side = RIGHT)

        self.buttonFrame = Frame(self.root, width = 750, height = 40, bg = "white")
        self.buttonFrame.pack(side = TOP, pady = 5)

        self.buttonFrameLeft = Frame(self.buttonFrame, width = 300, height = 40, bg = "white")
        self.buttonFrameMiddle = Label(self.buttonFrame, text = "", width = 19, bg = "white", font = ("Helvetica", 12, "bold"))
        self.buttonFrameRight = Frame(self.buttonFrame, width = 300, height = 40, bg = "white")
        self.buttonFrameLeft.pack(side = LEFT, pady = 5)
        self.buttonFrameMiddle.pack(side = LEFT)
        self.buttonFrameRight.pack(side = RIGHT, pady = 5)

        self.buttonFrameButtonAuto = Button(self.buttonFrameLeft, text = 'Autostart []', font = ("Helvetica", 14), command = self.root.quit, width = 14, height = 1, bg = "gray", fg = "white", state = DISABLED)
        self.buttonFrameButtonAuto.pack(side = LEFT, padx = 5)
        self.buttonFrameButtonConfirm = Button(self.buttonFrameLeft, text = 'Wert\nBestätigen', font = ("Helvetica", 8), command = self.nextState, width = 14, height = 2, bg = "gray", fg = "white")
        self.buttonFrameButtonConfirm.pack(side = LEFT, padx = 5)
        self.buttonFrameButtonBack = Button(self.buttonFrameRight, text = 'Zurück', font = ("Helvetica", 14), command = self.prevState, width = 10, height = 1, bg = "gray", fg = "white")
        self.buttonFrameButtonBack.pack(side = RIGHT, padx = 5)
        self.buttonFrameButtonClose = Button(self.buttonFrameRight, text = 'Abschließen', font = ("Helvetica", 14), command = self.exitApplication, height = 1, bg = "gray", fg = "white")
        self.buttonFrameButtonClose.pack(side = RIGHT, padx = 5)

        # adding the measure points to the header frame
        # add each object to a list for later adjustment
        i = 0
        for current in self.currents:
            temp = Label(self.valuesFrame, text = str(current), bg = "gray", fg = "white", font = ("Helvetica", 16),height = 1, width = 4)
            self.currentIds.append(temp)
            self.iStates.append(i)
            self.voltages.append(self.calcVoltage(current))
            self.xlabels.append(str(current))
            temp.pack(padx = 10, pady = 5, side = LEFT)
            print(self.voltages[i])
            #print(currentIds[i])
            i+=1
        
        for current in self.currents[::-1]:
            temp = Label(self.valuesFrame, text = str(current), bg = "gray", fg = "white", font = ("Helvetica", 16), height = 1, width = 4)
            self.currentIds.append(temp)
            self.iStates.append(len(currents)-i%len(currents)-1)
            self.voltages.append(self.calcVoltage(current))
            temp.pack(padx = 10, side = LEFT)
            self.xlabels.append(str(current))
            print(self.voltages[i])
            #print(currentIds[i])
            i+=1
        
        #####################################################################
        #### End layout                                                 #####
        #####################################################################
        
        # init the chart
        ax.plot(self.voltages, marker = 'o')
        ax.set_ylim(10, 25)
        ax.set_xlim(0, len(self.voltages)-1)
        ax.set_xticklabels(self.xlabels)
        ax.grid(axis = 'y', color = 'gray')
        line = FigureCanvasTkAgg(figure, self.chartFrame)
        line.get_tk_widget().pack()
        
    
    # helpter function to get the voltage based on the current
    def calcVoltage(self, current):
        return current*0.02+14

    # helper function for drawing the tolerance on the chart
    def drawSquare(self, voltage):
        y = 0.95*voltage
        x = self.getState() - 0.05*(self.iStates[self.getState()]+1)
        width = 0.1*(self.iStates[self.getState()]+1)
        height = 0.1*y
        ax.add_patch(Rectangle((x,y), width, height, linewidth = 2, edgecolor = 'yellow', facecolor = 'none'))
        
    # call back function for redrawing the chart and adjusting colors etc.
    def updateChart(self, arg):
        amps = self.scaler.get()
        volts = self.calcVoltage(amps)
        state = self.getState()
        # check if measurement is within tolerance
        self.checkMeasurementState(self.voltages[state],self.calcVoltage(amps))
        
        # adjust the color of the current measurement
        self.currentIds[state].config(bg = self.stateColor)
        
        # colort and values of voltages
        self.voltageActualLabel.config(fg = self.stateColor)
        self.voltageTargetLabel.config(fg = self.stateColor)
        self.voltageActualLabel['text'] = str(volts)+' V'
        self.voltageTargetLabel['text'] = str(self.voltages[state])+' V'
        
        # colort and values of the currents
        self.currentActualLabel.config(fg = self.stateColor)
        self.currentTargetLabel.config(fg = self.stateColor)
        self.currentActualLabel['text'] = str(amps)+' A'
        self.currentTargetLabel['text'] = str(self.xlabels[state])+' A'

        # clear the canvas and redraw
        ax.clear()
        
        # plot the reference trajectory
        ax.plot(self.voltages, marker = 'o', color = 'gray')
        
        # plot measured values
        if state > 0:
            for i in range(state):
                ax.plot(i, self.historyVoltages[i], 'o', color = self.historyColors[i])
        
        # plut current measurement of the voltage at the current state
        ax.plot(state,volts, 'o', color = self.stateColor)
        
        # tolerance square
        self.drawSquare(self.voltages[state])
        
        # set the chart options
        ax.set_ylim(10, 25)
        ax.set_xlim(0, len(self.voltages)-1)
        ax.set_xticklabels(self.xlabels)
        ax.grid(axis = 'y', color = 'gray')
        
    # what happens when click on "Wert bestätigen" 
    def nextState(self):
        if (self.state+1) < len(self.voltages):
            self.state += 1
            self.historyVoltages.append(self.calcVoltage(self.scaler.get()))
            self.historyColors.append(self.stateColor)        
            self.headingLabel['text'] = "Messpunkt "+str(self.state+1)
    
    # what happens when click on "zurück"
    def prevState(self):
        if self.state > 0:
            self.state -= 1
            self.historyColors.pop()
            self.historyVoltages.pop()
            self.headingLabel['text'] = "Messpunkt "+str(self.state+1)
                    
    # get the current state        
    def getState(self):
        return self.state

    def getCurrents(self):
        return self.currents
    
    # return the right color for the measurement
    # within tolerance: green
    # else: red
    def checkMeasurementState(self, target, actual):
        if abs(target-actual)/target <= 0.05:
            self.stateColor = 'green'
        else:
            self.stateColor = 'red'
    
    # setter and getter for the updateintervals of the chart
    def setIntervalMs(self, interval):
        self.updateIntervalMs = interval
        
    def getIntervalMs(self):
        return self.updateIntervalMs
    
    # game over...
    def exitApplication(self):
       self.slider.destroy()
       self.root.destroy()
    
    

# create an instance
app = WeldScannerCalibration()
app.setIntervalMs(200)

# set the callback function and polling period for updating the chart
ani = animation.FuncAnimation(figure, app.updateChart, interval = app.getIntervalMs())
mainloop()