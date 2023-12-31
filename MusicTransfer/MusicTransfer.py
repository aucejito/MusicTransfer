"""Welcome to Reflex! This file outlines the steps to create a basic app."""
import reflex as rx

import auth
from MusicTransfer import constants
from MusicTransfer.base_state import BasePageState
from rxconfig import config

docs_url = "https://reflex.dev/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"


def index() -> rx.Component:
    return rx.flex(
        rx.button_group(
            rx.cond(
                BasePageState.tidal_is_app_authenticated,
                rx.button(
                    "Signed in with Tidal",
                    color="black",
                    background_color="white",
                    style={"border": "0.15em solid black"},
                ),
                rx.button(
                    "Sign in with Tidal",
                    color="white",
                    background_color="black",
                    on_click=BasePageState.tidal_auth_url(),
                ),
            ),
            rx.cond(
                BasePageState.spotify_app_is_authenticated,
                rx.button(
                    "Signed in with Spotify",
                    color="#1DB954",
                    background_color="white",
                    style={"border": "0.15em solid #1DB954"},
                ),
                rx.button(
                    "Sign in with Spotify",
                    color="white",
                    background_color="#1DB954",
                    on_click=rx.redirect(
                        BasePageState.spotify_auth_url,
                        external=False,
                    ),
                ),
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
app.add_page(index, on_load=BasePageState.on_load)
app.compile()
