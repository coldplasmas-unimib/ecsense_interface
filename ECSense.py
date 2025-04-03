import PySimpleGUI as sg
from SerialInterface import SerialInterface
from datetime import datetime

class ECSense:

    def __init__(self, port, tag, axis, saver, ID):

        self.ID = ID
        self.port = port
        self.tag = tag
        self.saver = saver

        self.ser = SerialInterface( port )

        self.layout = [[
            sg.Frame(f"{tag} ({port})", [
                [sg.Text(f"Type: {self.ser.gas}, range {self.ser.maxrange} {self.ser.unit}, decimal places {self.ser.decimals}", font=('Helvetica', 7)),
                    sg.Button(f"X", key=f'sens:{ID}:delete')],
                # [sg.Text(f"{self.min:.1f} to {self.max:.1f} {self.unit}", font=(
                    # 'Helvetica', 7))],
                [sg.Text(f"...", key=f'sens:{ID}:current_value', font=(
                    'Helvetica', 18)), sg.Text(self.ser.unit)],                
                [sg.Text(f"...", key=f'sens:{ID}:temp', font=('Helvetica', 10)), sg.Text(f"...", key=f'sens:{ID}:humid', font=('Helvetica', 10))],                
            ], key = f'sens:{ID}' )
        ]]

        self.ser.startPooling()

        self.line, = axis.plot([], [], label=tag)

    def update_window(self, window):

        # Update current value
        window[f'sens:{self.ID}:current_value'].update(
            self.getLastValue( str = True ) )
        window[f'sens:{self.ID}:temp'].update(
            self.getLastTemp( str = True ) )
        window[f'sens:{self.ID}:humid'].update(
            self.getLastHumid( str = True ) )

        # Plot
        xs, ys = self.ser.getAllValues()
        xs = xs - datetime.now().timestamp() / 60.0
        self.line.set_data( xs, ys )

    def getLastValue(self, str=False):
        if (str):
            return f"{self.ser.getLastValue():.{self.ser.decimals}f}"
        return self.ser.getLastValue

    def getLastTemp(self, str=False):
        if (str):
            return f"{self.ser.getLastTemp():.2f}"
        return self.ser.getLastTemp()
    
    def getLastHumid(self, str=False):
        if (str):
            return f"{self.ser.getLastHumid():.2f}"
        return self.ser.getLastHumid()
    
    def getAllValues(self):
        return self.ser.getAllValues()

    def lastI(self):
        return self.ser.i
