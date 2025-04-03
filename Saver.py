import os
from os.path import exists
from datetime import datetime
import PySimpleGUI as sg
import threading
import numpy as np
import time

class Saver:

    def __init__(self, connectedSens):

        self.folder = os.getcwd() + "/" + datetime.now().strftime("%Y%m%d")
        self.connectedSens = connectedSens

        self.layout = [
                sg.Button("Registra", key="saver:record"),
                sg.Button("Apri cartella", key="saver:viewFolder"),
                sg.Text("", key="saver:status")
        ]

        self.saving = False


    def parse_events(self, event, values, window):

        if event == "saver:record":
            if self.saving:
                self.endSaving(window)
            else:
                self.beginSaving(window)

        if event == "saver:viewFolder":
            os.startfile( self.folder )
    
    def beginSaving(self, window):
        
        os.makedirs( self.folder, exist_ok=True )

        progr = 0
        while( exists( self.folder + f"/Sens{progr:04d}.csv" ) ):
            progr += 1
        
        self.filename = self.folder + f"/Sens{progr:04d}.csv"

        self.saving = True
        self.file = open( self.filename, "w", buffering = 1 )

        self.file.write("Time[s]")
        for sens in self.connectedSens:
            self.file.write(f",{sens.tag}-{sens.ser.gas}-{sens.ser.maxrange}{sens.ser.unit}")
            self.file.write(f",{sens.tag}-temp-C")
            self.file.write(f",{sens.tag}-humid-RH%")
        self.file.write('\n')

        self.thread = threading.Thread(target=self.save_thrd)
        self.thread.start()

        window["saver:status"].update(f"Salvataggio in {self.filename}")
        window["saver:record"].update("Stop")



    def endSaving(self, window):

        self.saving = False
        self.thread.join()

        self.file.close()

        window["saver:status"].update("")
        window["saver:record"].update("Registra")


    def save_thrd(self):

        last_i = { i: sens.lastI() for i, sens in enumerate( self.connectedSens ) }

        while( self.saving ):
            allUpdated = not np.any( [ last_i[i] == sens.lastI() for i, sens in enumerate( self.connectedSens ) ] )

            if( not allUpdated ):
                time.sleep(0.1)
                continue
            
            self.file.write( f"{datetime.now().timestamp():.4f}")
            for i, sens in enumerate( self.connectedSens ):
                self.file.write( "," + sens.getLastValue( str = True ) )
                self.file.write( "," + sens.getLastTemp( str = True ) )
                self.file.write( "," + sens.getLastHumid( str = True ) )
                last_i[ i ] = sens.lastI()
            self.file.write( '\n' )