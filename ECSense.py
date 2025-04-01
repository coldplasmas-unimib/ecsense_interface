import PySimpleGUI as sg
from SerialInterface import SerialInterface

class ECSense:

    def __init__(self, port, gas, tag, axis, saver, ID):

        self.ID = ID
        self.port = port
        self.tag = tag
        self.saver = saver

        self.ser = SerialInterface( port )

        self.layout = [[
            sg.Frame(f"{tag} ({gas}, {port})", [
                [sg.Text(f"Type: {self.ser.gas}, range {self.ser.maxrange} {self.ser.unit}, decimal places {self.ser.decimals}", font=('Helvetica', 7)),
                    sg.Button(f"X", key=f'sens:{ID}:delete')],
                # [sg.Text(f"{self.min:.1f} to {self.max:.1f} {self.unit}", font=(
                    # 'Helvetica', 7))],
                [sg.Text(f"...", key=f'sens:{ID}:current_value', font=(
                    'Helvetica', 18)), sg.Text(self.unit)],                
            ], key = f'sens:{ID}' )
        ]]

        self.ser.startPooling()

        self.line, = axis.plot([], [], label=tag)

    def update_window(self, window):

        # Update current value
        window[f'sens:{self.ID}:current_value'].update(
            self.getLastValue( str = True ) )

        # Plot
        self.line.set_data( *self.ser.getAllValues() )

    def getLastValue(self, str=False):
        if (str):
            return f"{self.ser.getLastValue():.{self.ser.decimals}f}"
        return self.ser.getLastValue

    def getAllValues(self):
        return self.ser.getAllValues()
