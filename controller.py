from windows.main.window import MainWindow
from windows.gendiagram.window import GenerateDiagramWindow


class Controller:
    def __init__(self):
        pass

    def select_forms(self, text):
        if text == "main":
            self.main_window = MainWindow()
            self.main_window.switch_window.connect(self.select_forms)
            self.main_window.show()

        if text == "main>generate_diagram":
            self.generate_diagram = GenerateDiagramWindow()
            self.generate_diagram.switch_window.connect(self.select_forms)
            self.generate_diagram.show()
            self.main_window.close()

        if text == "main<generate_diagram":
            self.main_window = MainWindow()
            self.main_window.switch_window.connect(self.select_forms)
            self.main_window.show()
            self.generate_diagram.close()
