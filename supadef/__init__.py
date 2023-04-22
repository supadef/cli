from typing import Dict, List, Optional, Any
from decimal import Decimal
from uuid import UUID


def compose(*args):
    """
    Define a UX to invoke the function
    :param args: UI to compose
    :return:
    """
    def g(f):
        return f
    return g

def returns(*args):
    """
    Define a UX to return, after invoking the function
    """
    def g(f):
        return f
    return g

def text_input(arg: str, hidden: bool = False):
    """
    Text Input
    :param arg: The name of the argument that this input will be passed into
    :param hidden: If True, will hide the input password-style
    """
    pass


def button(title: str, action: str = 'run', color: str = 'theme:action'):
    """
    Button. Perform an action
    :param title: The title of the button
    :param action: The action to take when this button is pressed. run = run the function, goto:[func] opens another function
    :param color: The color of the button
    """
    pass


def card(child: Any, color: str = 'theme:primary'):
    """
    Card: display prominent text
    :param child: The inner UI component
    :param color: The background color of the card
    """
    pass


def title(title: str, color: str = 'theme:text_on_primary'):
    """
    Display prominent text
    :param title: The text to display
    :param color: The color of the text
    """
    pass


