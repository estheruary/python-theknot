# python-theknot

Are you using The Knot for your wedding registry? Are you infuriated at the
barely working bookmarklet they provide you to add things to your registry that
aren't on one of the major department stores? Do you wish you could set custom
images to the items on your registry that aren't the one's on the site?

*Well say no more!*

This project, `python-theknot` provides a CLI tool that gives you all the power
of the extension but you can just supply all the values yourself.

## Installation

```bash
pip install theknot
```

## Usage

```bash
# Tests and saves your creds in ~/.config/theknot/config.json.
theknot login
Email: meandmywifu@gmail.com
Password: ******

theknot add \
  --name="The Blood of My Enemies" \
  --store-name="Target" \
  --item-link="https://www.target.com/p/the-blood-of-my-enemies/-/A-46793820" \
  --image-link="https://some-PUBLIC-image.site/img/2492333" \
  --price=799 \
  --num=1

# Deletes the file ~/.config/theknot/config.json.
theknot logout
```
