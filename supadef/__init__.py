
def compose(*args, returns=None):
    """
    Main wrapper to begin composing flows
    :param args: UI to compose
    :param returns: UI from result of function
    :return:
    """
    pass


def text_input(arg: str, hidden=False):
    """
    Text Input (function argument)
    :param arg: the argument this input will be passed into
    :param hidden: if True, will hide the input password-style
    :return:
    """
    pass


def button(title: str, action='run', color='theme:action'):
    """
    UI Button (run function, go to another function)
    :param title: title of the button
    :param action: run = run the function, goto:[func] opens another function
    :param color: color of the button
    :return:
    """
    pass


def card(title: str, color='theme:action'):
    """
    UI Card (display prominent Text)
    :param title: text to display
    :param color: color of the button
    :return:
    """
    pass

