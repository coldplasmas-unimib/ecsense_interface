import PySimpleGUI as sg
from serial.tools import list_ports
from SerialInterface import SerialInterface


class AvailablePort:

    def __init__(self, port):
        self.port = port
        self.data = port + " - " + SerialInterface.testPort(port)

    def __str__(self):
        return self.data


class AddSensWindow:

    def __init__(self, alreadyConn):
        self.layout = [[
            sg.Column([
                [sg.Text("Aggiungi sensore", font=('Helvetica', 20))],
                [sg.Text("Porta:")],
                [sg.Combo([], key='addSens:ports_combo',
                          expand_x=True, size=(50, 10), readonly=True), sg.Button("↻", key="addSens:refresh")],
                [sg.Text("Nome:")],
                [sg.Input(
                    default_text=f"Sens{len(alreadyConn)+1}", key="addSens:tag")],
                [sg.Button('Salva', key='addSens:save'), sg.Text('Errore', text_color='red',
                                                                 key='addSens:error', visible=False)]
            ])
        ]]

        self.window = sg.Window(title="Aggiungi sensore",
                                layout=self.layout)

        self.alreadyConn = alreadyConn

    def refresh_ports(self):
        ports = [AvailablePort(p.device) for p in list_ports.comports(
        ) if p.device not in self.alreadyConn]
        self.window['addSens:ports_combo'].update(
            values=[p for p in ports], value=(ports[0] if len(ports) > 0 else ""))

    def run(self):
        self.window.finalize()
        self.refresh_ports()

        return self.loop()

    def loop(self):
        while True:
            event, values = self.window.read(timeout=100)

            if event == 'addSens:refresh':
                self.refresh_ports()

            if event == sg.WIN_CLOSED:
                return False

            if event == 'addSens:save':

                # Check for port
                port = getattr(values['addSens:ports_combo'], 'port', "")

                if port not in [p.device for p in list_ports.comports()]:
                    self.showError('Porta non valida')
                    continue
                if port in [self.alreadyConn]:
                    self.showError('Porta già registrata')
                    continue

                # Load the tag
                tag = values['addSens:tag']

                self.window.close()
                return {
                    'port': port,
                    'tag': tag
                }

    def showError(self, error):
        self.window['addSens:error'].update(error, visible=True)
