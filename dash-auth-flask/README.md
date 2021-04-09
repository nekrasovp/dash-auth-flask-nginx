# dash-auth-flask
Flask authentication for [Dash](https://dash.plotly.com/).

## Features
Landing pages and functions to run the entire authentication process:
- home
- login
- logout
- register
- forgot password
- change password

This uses `dash-auth-flow` as auth process template, 
check this great repository [dash-auth-flow](https://github.com/russellromney/dash-auth-flow), 
which uses `flask-login` on the backend, 
using some code from the very 
useful [dash-flask-login](https://github.com/RafaelMiquelino/dash-flask-login). 

## Built-in dbsqlite3 backend

Data is held in `users.db`. File is created if not existed and test@test.com\test user created
 for testing.

```bash
python -m venv venv
source ./venv/bin/activate
python -m pip install requirements.txt
python create_tables.py
python app.py
```

## Notes:

- this uses MailJet as the email API. You need a [free MailJet API key](https://www.mailjet.com/email-api/)
- your send-from email and API key/secret need to be entered in `config/keys.py`
- if you want to use something else, change the `send_password_key` function in `utilities/auth.py`
- add pages in `pages/`.
- the app's basic layout and routing happens in `app.py`
- app is created and auth is built in `server.py`
- config is in `utilities/config.txt` and `utilities/config.py`
