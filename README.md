## Installation on Windows
1) Download https://bootstrap.pypa.io/get-pip.py
2) `python get-pip.py`
3) `pip install virtualenv`
4) `virtualenv venv` anywhere not in git repository (preferably same level as git repository root folder)
5) Your project folder now has two folders: `venv` and `git_root_folder`

## Install dependencies
1) Activate environment: `call /venv/Scripts/activate.bat`
2) `pip install -r setup/requirements/txt`
