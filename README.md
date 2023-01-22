# Forum
A simple web forum written in Python.

## Features

- New users can request access which has to be granted by an admin user.
- The admin users can also give permissions to other users, e.g. to only access and write to the forum, or to also have admin permissions.
- Posts are written in Topics and organized into Categories.
- Posts can be formatted using different BBCodes.

## Configuration

Configure the styling of the forum, especially the [logo](static/images/logo.png), to give your own forum a more unique look and feel.

## Setup

### Get the code
`git clone https://github.com/ColdIV/forum.git` and enter the directory.

### Create a virtual development environment

E.g. by using `venv`: `python -m venv env`

### Enter the virtual environment:

`source env/bin/activate` <br>
If you use Windows, run `.\env\Scripts\activate`

### Install the required dependencies inside the virtual environment
`pip3 install -r requirements.txt`

### Run the server
`python3 app.py dev` for the development server <br>
`python3 app.py` for the production server <br>
On the first run, you will be asked to register an **Admin** user. 

### If CSS has been changed
`python -m scss < static/styles/styles.scss -o static/styles/styles-min.css -I static/styles/` <br>
For changes in admin.scss: <br>
`python -m scss < static/styles/admin.scss -o static/styles/admin-min.css -I static/styles/` <br>
If you use Windows, run `build-css.bat` for both.

## Contributing to the project

Thank you for your interest! Please see our [contribution guide](CONTRIBUTING.md) for more information on how you can help improving the forum.








