from dominate import tags
from flask import url_for
from flask_login import current_user
from flask_nav.renderers import Renderer
from flask_nav.elements import Navbar, View

from app import nav

Navigation_logged_in = Navbar('',  # empty title
                              View('Upload', 'upload'),
                              View('Files', 'list_files'),
                              View('Log entries', 'show_log_entries')
                              )

Navigation_logged_out = Navbar('')  # empty title


@nav.navigation(id='top')
def top():
    if current_user.is_authenticated:
        return Navigation_logged_in
    else:
        return Navigation_logged_out


def create_login_logout_btn(logged_in):
    button = tags.a(_class='btn btn-light')
    if logged_in:
        button.add('Logout')
        button['href'] = f"{url_for('logout')}"
    else:
        button.add('Sign in')
        button['href'] = f"{url_for('login')}"

    return button


# modified from SimpleRenderer from flask-nav, which is licensed as follows:
#       Copyright (c) 2015 Marc Brinkmann
#
#       Permission is hereby granted, free of charge, to any person obtaining a
#       copy of this software and associated documentation files (the "Software"),
#       to deal in the Software without restriction, including without limitation
#       the rights to use, copy, modify, merge, publish, distribute, sublicense,
#       and/or sell copies of the Software, and to permit persons to whom the
#       Software is furnished to do so, subject to the following conditions:
#
#       The above copyright notice and this permission notice shall be included in
#       all copies or substantial portions of the Software.
#
#       THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#       IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#       FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#       AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#       LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#       FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#       DEALINGS IN THE SOFTWARE.
class BootstrapRenderer(Renderer):
    def __init__(self):
        pass

    def visit_Link(self, node):
        return tags.a(node.text, _class='nav-item nav-link', href=node.get_url())

    # see https://getbootstrap.com/docs/4.4/components/navbar/
    def visit_Navbar(self, node):
        cont = tags.nav(_class='navbar sticky-top navbar-expand-sm navbar-dark bg-secondary')

        if current_user.is_authenticated:  # navbar is empty if not logged in, therefore no toggle button needed
            btn_toggle_kwargs = {
                'class': 'navbar-toggler', 'type': 'button', 'data-toggle': 'collapse',
                'data-target': '#navbarCollapseDiv', 'aria-controls': 'navbarCollapseDiv', 'aria-expanded': 'false',
                'aria-label': 'Toggle navigation'
            }
            btn_toggle = cont.add(tags.button(**btn_toggle_kwargs))
            btn_toggle.add(tags.span(_class='navbar-toggler-icon'))
        else:
            cont['class'] += ' display-flex justify-content-end'  # so that the sign in button is always on the right

        div_coll = cont.add(tags.div(_class='collapse navbar-collapse', id='navbarCollapseDiv'))
        div_nav  = div_coll.add(tags.div(_class='navbar-nav'))

        for item in node.items:
            div_nav.add(self.visit(item))

        cont.add(create_login_logout_btn(current_user.is_authenticated))

        return cont

    def visit_View(self, node):
        kwargs = {'_class': 'nav-item nav-link'}
        if node.active:
            kwargs['_class'] += ' active'
        return tags.a(node.text, href=node.get_url(), title=node.text, **kwargs)

    def visit_Text(self, node):
        return tags.span(node.text, _class='nav-text')
