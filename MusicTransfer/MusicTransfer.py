"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import reflex as rx

import auth
from rxconfig import config

docs_url = "https://reflex.dev/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    """The app state."""

    pass


class TidalButtonState(rx.State):
    is_logged = False
    text_value = "Sign in with Tidal"

    def login(self):
        if self.is_logged:
            return None
        self.session = auth.open_tidal_session()
        if self.session:
            self.is_logged = True
            print("Tidal Session opened successfully")

        self.text_value = "Signed in with Tidal"
        return None


def index() -> rx.Component:
    return rx.flex(
        rx.button_group(
            rx.button(
                TidalButtonState.text_value,
                color="white",
                background_color="black",
                on_click=TidalButtonState.login,
            ),
            margin="0.5em",
            style={"position": "absolute", "right": "0"},
        ),
        rx.vstack(
            rx.heading("Welcome to Reflex!", font_size="2em"),
            rx.box(
                "Get started by editing ",
                rx.code(
                    filename,
                    font_size="1em",
                ),
            ),
            rx.link(
                "Check out our docs!",
                href=docs_url,
                border="0.1em solid",
                padding="0.5em",
                border_radius="0.5em",
                _hover={
                    "color": rx.color_mode_cond(
                        light="rgb(107,99,246)",
                        dark="rgb(179, 175, 255)",
                    )
                },
            ),
            spacing="1.5em",
            font_size="2em",
            padding_top="10%",
        ),
        direction="column",
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.compile()
