import PySimpleGUI as sg
import AddSensWindow
import Saver
import ECSense
from serial.serialutil import SerialException

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')


class MainWindow:

    def __init__(self):

        self.Sens_ID = 0
        self.connectedSens = []

        self.saver = Saver.Saver(self.connectedSens)


        self.layout = [[
            sg.Column([
                [sg.Text("0", key="main:cnum"), sg.Text("Sensori connessi")],
                [sg.Column([], key="main:col")],
                [sg.Button("Aggiungi sensore", key='main:addSens')],
                self.saver.layout,
                [sg.Text("L. Zampieri - 04/2025", font=('Helvetica', 7))]
            ]),
            sg.Canvas(key='canvas')
        ]]

        sg.theme('Dark')
        self.window = sg.Window(title="Sensori ECSense",
                                layout=self.layout, finalize=True)

        self.init_plot()

        if (len(self.connectedSens) == 0):
            self.addSens()

    def init_plot(self):
        self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.axis = self.fig.add_subplot(111)
        self.tkcanvas = FigureCanvasTkAgg(
            self.fig, self.window['canvas'].TKCanvas)
        self.tkcanvas.draw()
        self.tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)

        self.axis.set_xlim(- 5, 0)
        self.axis.set_xlabel("Time [min]")

    def loop(self):
        while True:
            event, values = self.window.read(timeout=100)

            if (event == 'main:addSens'):
                if( self.saver.saving ):
                    continue
                self.addSens()

            if event == sg.WIN_CLOSED:
                return

            for i, id in enumerate( [ i.ID for i in self.connectedSens ] ):
                if event == f'sens:{id}:delete':
                    sens = self.connectedSens.pop( i )
                    del sens
                    self.window[f'sens:{id}'].update( visible = False )

            self.saver.parse_events(event, values, self.window)
            self.confsaver.parse_events(event, values, self.window)

            if( len( self.connectedSens ) > 0 ):

                for Sens in self.connectedSens:
                    Sens.update_window(self.window)

                self.axis.relim()  # scale the y scale
                self.axis.autoscale_view()  # scale the y scale
                self.tkcanvas.draw()

    def addSens(self):
        amw = AddSensWindow.AddSensWindow(
            alreadyConn=[d.port for d in self.connectedSens])
        newSens = amw.run()
        if (newSens):
            self.saveSens(**newSens)

    def saveSens(self, port, gas, tag):
        try:
            self.Sens_ID += 1
            newSens = ECSense.Sens(port, gas, tag, axis=self.axis,
                             saver=self.saver, ID=self.Sens_ID)
        except SerialException as e:
            sg.popup_error("Impossibile connettersi alla porta")
            return

        self.connectedSens.append(newSens)
        self.window.extend_layout(self.window['main:col'], newSens.layout)
        newSens.bind_events(self.window)
        self.window['main:cnum'].update(len(self.connectedSens))
        self.axis.legend()
