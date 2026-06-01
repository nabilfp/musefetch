from textual.app import App
from musefetch.ui.screens import MainScreen

class MusefetchApp(App):
    CSS_PATH = "ui/app.tcss"
    TITLE = "musefetch"
    SUB_TITLE = "yt music for termux"
    def on_mount(self):
        self.push_screen(MainScreen())

def main():
    MusefetchApp().run()

if __name__ == "__main__":
    main()
