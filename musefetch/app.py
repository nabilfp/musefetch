from textual.app import App
from musefetch.ui.screens import MainScreen


class MusefetchApp(App):
    """Termux-native TUI for YT Music playlist downloads."""
    CSS_PATH = "ui/app.tcss"
    TITLE = "musefetch"
    SUB_TITLE = "yt music for termux"

    def on_mount(self):
        self.push_screen(MainScreen())


def main():
    MusefetchApp().run()


if __name__ == "__main__":
    main()
