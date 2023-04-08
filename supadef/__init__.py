def compose(*args, returns=None):
    """
    Main wrapper to begin composing flows
    :param args: UI to compose
    :param returns: UI from result of function
    :return:
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


def card(title: str, color: str = 'theme:primary'):
    """
    Card: display prominent text
    :param title: The text to display
    :param color: The background color of the card
    """
    pass


