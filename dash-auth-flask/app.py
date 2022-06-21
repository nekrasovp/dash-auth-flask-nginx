# index page
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from flask import redirect
from server import app, server
from flask_login import logout_user, current_user

# app pages
from pages import (home, profile, page1)

# app authentication 
from pages.auth_pages import (login, register, forgot_password, change_password)


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#333",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Menu", className="display-4"),
        html.Hr(),
        html.P(
            "Subtitle", className="lead"
<<<<<<< HEAD
        ),
        dbc.Nav(
            [
                    dbc.NavItem(dbc.NavLink("Home", href="/home")),
                    dbc.NavItem(dbc.NavLink("Page1", href="/page1")),
                    dbc.NavItem(dbc.NavLink("Profile", id='user-name', href='/profile')),
                    dbc.NavItem(dbc.NavLink('Login',id='user-action',href='/login'))
            ],
            vertical=True,
            pills=True,
        ),
=======
        ),
        dbc.Nav(
            [
                    dbc.NavItem(dbc.NavLink("Home", href="/home", external_link=True)),
                    dbc.NavItem(dbc.NavLink("Page1", href="/page1", external_link=True)),
                    dbc.NavItem(dbc.NavLink(id='user-name',href='/profile', external_link=True)),
                    dbc.NavItem(dbc.NavLink('Login',id='user-action',href='Login', external_link=True))
            ],
            vertical=True,
            pills=True,
        ),
>>>>>>> ef45c25b7ab23df84bccff195c5b070aa6432d32
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="base-url"), sidebar, content])

# header = dbc.Navbar(
#     dbc.Container(
#         [
#             dbc.NavbarBrand("Dash Auth Flask", href="/home"),
#             dbc.Nav(
#                 [
<<<<<<< HEAD
#                     dbc.NavItem(dbc.NavLink("Home", href="/home")),
#                     dbc.NavItem(dbc.NavLink("Page1", href="/page1")),
#                     dbc.NavItem(dbc.NavLink(id='user-name',href='/profile')),
#                     dbc.NavItem(dbc.NavLink('Login',id='user-action',href='Login'))
=======
#                     dbc.NavItem(dbc.NavLink("Home", href="/home", external_link=True)),
#                     dbc.NavItem(dbc.NavLink("Page1", href="/page1", external_link=True)),
#                     dbc.NavItem(dbc.NavLink(id='user-name',href='/profile', external_link=True)),
#                     dbc.NavItem(dbc.NavLink('Login',id='user-action',href='Login', external_link=True))
>>>>>>> ef45c25b7ab23df84bccff195c5b070aa6432d32
#                 ]
#             )
#         ]
#     ),
#     className="mb-5",
# )



# app.layout = html.Div(
#     [
#         header,
#         html.Div(
#             [
#                 dbc.Container(
#                     id='page-content'
#                 )
#             ]
#         ),
#         dcc.Location(id='base-url', refresh=False)
#     ]
# )


@app.callback(
    Output('page-content', 'children'),
    [Input('base-url', 'pathname')])
def router(pathname):
    '''
    routes to correct page based on pathname
    '''
    print('routing to',pathname)
    # auth pages
    if pathname == '/login':
        if not current_user.is_authenticated:
            return login.layout()
    elif pathname =='/register':
        if not current_user.is_authenticated:
            return register.layout()
    elif pathname == '/change':
        if current_user.is_authenticated:
            return change_password.layout()
    elif pathname == '/forgot':
        if current_user.is_authenticated:
            return forgot_password.layout()
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
    
    # app pages
    elif pathname == '/' or pathname=='/home' or pathname=='/home':
        if current_user.is_authenticated:
            return home.layout()
    elif pathname == '/profile' or pathname=='/profile':
        if current_user.is_authenticated:
            return profile.layout()
    elif pathname == '/page1' or pathname=='/page1':
        if current_user.is_authenticated:
            return page1.layout()

    # DEFAULT LOGGED IN: /home
    if current_user.is_authenticated:
        return home.layout()
    
    # DEFAULT NOT LOGGED IN: /login
    return login.layout()





@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def profile_link(content):
    '''
    returns a navbar link to the user profile if the user is authenticated
    '''
    if current_user.is_authenticated:
        return html.Div(current_user.first)
    else:
        return ''


@app.callback(
    [Output('user-action', 'children'),
     Output('user-action','href')],
    [Input('page-content', 'children')])
def user_logout(input1):
    '''
    returns a navbar link to /logout or /login, respectively, if the user is authenticated or not
    '''
    if current_user.is_authenticated:
        return 'Logout', '/logout'
    else:
        return 'Login', '/login'



if __name__ == '__main__':
    app.run_server(debug=False, port=8000)
