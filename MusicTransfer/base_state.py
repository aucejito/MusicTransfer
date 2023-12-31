import asyncio
import base64
import json
import os
import random
import string
import threading
import urllib
import webbrowser

import reflex as rx
import requests
import spotipy
import tidalapi

from MusicTransfer import constants

from .utils import add_token_expiry_time, token_expired


class BasePageState(rx.State):
    ###########
    # Spotify #
    ###########
    @rx.var
    def callback_code_and_state(self) -> tuple[str]:
        """Code and state from callback uri after redirect"""
        args = self.router.page.params
        code = args.get("code", None)
        state = args.get("state", None)
        return code, state

    code_req_state: str = "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(16)
    )

    @rx.var
    def spotify_auth_url(self) -> str:
        """Url to take user to Spotify authentication page"""
        scope = constants.SPOTIFY_API_SCOPES

        params = {
            "response_type": "code",
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "scope": scope,
            "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI"),
            "state": self.code_req_state,
        }

        auth_url = (
            "https://accounts.spotify.com/authorize?"
            + urllib.parse.urlencode(params)
        )
        return auth_url

    spotify_auth_token_json: str = rx.LocalStorage(
        "", name="spotify_auth_token"
    )

    def get_auth_token_from_callback(self):
        """Request an authentication token from Spotify based on the code
        provided in the redirect. If the state string provided in tbe redirect
        does not match that provided for the authentication url, do not accept
        it. Update state var with provided auth token
        """
        print("Getting spotify authentication token")
        code, state = self.callback_code_and_state
        if state == self.code_req_state:
            auth_options = {
                "url": "https://accounts.spotify.com/api/token",
                "data": {
                    "code": code,
                    "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI"),
                    "grant_type": "authorization_code",
                },
                "headers": {
                    "content-type": "application/x-www-form-urlencoded",
                    "Authorization": "Basic "
                    + base64.b64encode(
                        (
                            constants.SPOTIFY_CLIENT_ID
                            + ":"
                            + constants.SPOTIFY_CLIENT_SECRET
                        ).encode()
                    ).decode("utf-8"),
                },
            }

            response = requests.post(
                auth_options["url"],
                data=auth_options["data"],
                headers=auth_options["headers"],
            )

            enriched_response_dict = add_token_expiry_time(response.json())
            self.spotify_auth_token_json = json.dumps(enriched_response_dict)

    def _refresh_auth_token(self):
        """Use authentication token's 'refresh_token' property to request a new
        spotify authenticatioun token; update the state var accordingly
        """
        print("Refreshing Spotify authentication token")
        refresh_token = json.loads(self.spotify_auth_token_json)[
            "refresh_token"
        ]
        auth_options = {
            "url": "https://accounts.spotify.com/api/token",
            "data": {
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            "headers": {
                "content-type": "application/x-www-form-urlencoded",
                "Authorization": "Basic "
                + base64.b64encode(
                    (
                        constants.SPOTIFY_CLIENT_ID
                        + ":"
                        + constants.SPOTIFY_CLIENT_SECRET
                    ).encode()
                ).decode("utf-8"),
            },
        }

        response = requests.post(
            auth_options["url"],
            data=auth_options["data"],
            headers=auth_options["headers"],
        )

        enriched_response_dict = {
            **add_token_expiry_time(response.json()),
            "refresh_token": refresh_token,
        }
        self.spotify_auth_token_json = json.dumps(enriched_response_dict)

    @rx.var
    def spotify_app_is_authenticated(self) -> bool:
        return len(self.spotify_auth_token_json) > 0

    def get_sp(self) -> spotipy.Spotify:
        """Get a spotify instance"""
        if self.spotify_app_is_authenticated:
            return spotipy.Spotify(
                auth=json.loads(self.spotify_auth_token_json)["access_token"]
            )

    def on_load(self):
        if not self.spotify_app_is_authenticated:
            if self.callback_code_and_state != (None, None):
                self.get_auth_token_from_callback()

        else:
            if token_expired(json.loads(self.spotify_auth_token_json)):
                self._refresh_auth_token()

    #########
    # Tidal #
    #########
    tidal_auth_token_json: str = rx.LocalStorage("", name="tidal_auth_token")

    @rx.var
    def tidal_is_app_authenticated(self) -> bool:
        return len(self.tidal_auth_token_json) > 0

    def finish_tidal_auth(self, future, session):
        future.result()
        self.tidal_auth_token_json = json.dumps(
            {
                "session_id": session.session_id,
                "token_type": session.token_type,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
            },
        )

    def tidal_auth_url(self) -> rx.event.EventSpec:
        session = tidalapi.Session()
        login, future = session.login_oauth()
        print("Login with the webbrowser: " + login.verification_uri_complete)
        url = login.verification_uri_complete
        if not url.startswith("https://"):
            url = "https://" + url
        thread = threading.Thread(
            target=self.finish_tidal_auth, args=(future, session)
        )
        thread.start()
        return rx.redirect(url, external=True)

    def get_tidal_auth_token(self):
        return
