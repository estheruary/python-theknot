import json
from pathlib import Path
import sys
from typing import Annotated, Final, Optional, TypedDict
import requests
import os
import xdg

from typer import Typer, Option
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from theknot.exceptions import InvalidEmailOrPassword


DEFAULT_THEKNOT_API_KEY: Final[str] = "bLdY7wHVUjKBk3kZJkB0Gs5BcziVi2dn"
CONFIG_DIR: Final[Path] = xdg.XDG_CONFIG_HOME / "theknot"
CONFIG_FILE: Final[Path] = CONFIG_DIR / "config.json"
app = Typer()


class TheKnotConfig(TypedDict):
    email: str
    password: str
    api_key: str


def load_config() -> Optional[TheKnotConfig]:
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as cfg:
            return json.load(cfg)
    except (IOError, OSError):
        return None


def get_session(email: str, password: str, api_key: str):
    try:
        res = requests.post(
            "https://membership-api.theknot.com/sessions",
            params={"apikey": api_key},
            json={
                "sessions": {
                    "email": email,
                    "password": password,
                    "api_key": api_key,
                }
            },
        )
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise InvalidEmailOrPassword("TheKnot rejected your email/password") from e
        else:
            raise


@app.command("login")
def login(
    email: Annotated[str, Option(prompt=True)],
    password: Annotated[str, Option(prompt=True, hide_input=True)],
    api_key: Annotated[str, Option(envvar="THEKNOT_API_KEY")] = DEFAULT_THEKNOT_API_KEY,
):
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as p:
        t = p.add_task("Logging In")
        try:
            get_session(email, password, api_key)
        except InvalidEmailOrPassword:
            p.remove_task(t)
            print("[red]Error[/red]: TheKnot said your email/password was incorrect.")
            exit(1)

        p.add_task("Storing Creds")
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with CONFIG_FILE.open("w", encoding="utf-8") as cfg:
            json.dump({"email": email, "password": password, "api_key": api_key}, cfg, indent=2, sort_keys=True)


@app.command("logout")
def logout():
    CONFIG_FILE.unlink()


@app.command("add")
def add_to_registry(
        name: Annotated[str, Option()],
        store_name: Annotated[str, Option()],
        item_link: Annotated[str, Option()],
        image_link: Annotated[str, Option()],
        price: Annotated[str, Option()], 
        num: int = 1):
    if not (cfg := load_config()):
        print(f"[red]Error[/red]: You must run `{sys.argv[0]} login` first.")
        exit(1)

    sess = get_session(**cfg)
    token = sess["token"]
    member = sess["links"]["member"]

    res = requests.post(
        f"https://registry-gifts-api.regsvcs.theknot.com/{member}/registry-items",
        headers={
            "Membership-Session-Token": token,
        },
        json={
            "type": "UNIVERSAL_REGISTRY_PRODUCT",
            "imageUrls": [image_link],
            "name": name,
            "numRequested": num,
            "priceCents": price,
            "registryId": member,
            "storeName": store_name,
            "productUrl": item_link,
        },
    )
    res.raise_for_status()

    print("[green]Done[/green]!")


def main():
    app()


if __name__ == "__main__":
    main()
