from flask_login import current_user
from flask_nav.elements import Navbar, View

from app import nav

Navigation_logged_in = Navbar('',
                              View('Upload', 'upload'),
                              View('Files', 'list_files'),
                              View('Logout', 'logout')
                              )

Navigation_logged_out = Navbar('',
                               View('Upload', 'upload'),
                               View('Files', 'list_files'),
                               View('Sign In', 'login')
                               )


@nav.navigation(id='top')
def top():
    if current_user.is_authenticated:
        return Navigation_logged_in
    else:
        return Navigation_logged_out
