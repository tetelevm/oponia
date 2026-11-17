from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Static


class OponiaApp(App):
    TITLE = "Oponia"
    BINDINGS = [("q", "quit", "Quit")]
    CSS = """
    Screen { align: center middle; }
    Static { width: auto; margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hello, world! Welcome to Oponia.")
        yield Button("Quit", id="quit", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#quit")
    def quit_clicked(self) -> None:
        self.exit()


if __name__ == "__main__":
    OponiaApp().run()
