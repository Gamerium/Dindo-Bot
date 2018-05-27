# The Windows native message box.

import sys
import ctypes  # An included library with Python install.




MB_OK = 0x0
MB_OKCANCEL = 0x1
MB_ABORTRETRYIGNORE = 0x2
MB_YESNOCANCEL = 0x3
MB_YESNO = 0x4
MB_RETRYCANCEL = 0x5

MB_ICONHAND = MB_ICONSTOP = MB_ICONERRPR = 0x10
MB_ICONQUESTION = 0x20
MB_ICONEXCLAIMATION = 0x30
MB_ICONASTERISK = MB_ICONINFOMRAITON = 0x40

MB_DEFAULTBUTTON1 = 0x0
MB_DEFAULTBUTTON2 = 0x100
MB_DEFAULTBUTTON3 = 0x200
MB_DEFAULTBUTTON4 = 0x300

MB_SETFOREGROUND = 0x10000
MB_TOPMOST = 0x40000

runningOnPython2 = sys.version_info[0] == 2



if runningOnPython2:
    messageBoxFunc = ctypes.windll.user32.MessageBoxA
else: # Python 3 functions.
    messageBoxFunc = ctypes.windll.user32.MessageBoxW


def alert(text='', title='', button='OK'):
    """Displays a simple message box with text and a single OK button. Returns the text of the button clicked on."""
    messageBoxFunc(0, text, title, MB_OK | MB_SETFOREGROUND | MB_TOPMOST)
    return button

def confirm(text='', title='', buttons=['OK', 'Cancel']):
    """Displays a message box with OK and Cancel buttons. Number and text of buttons can be customized. Returns the text of the button clicked on."""
    retVal = messageBoxFunc(0, text, title, MB_OKCANCEL | MB_ICONQUESTION | MB_SETFOREGROUND | MB_TOPMOST)
    if retVal == 1 or len(buttons) == 1:
        return buttons[0]
    elif retVal == 2:
        return buttons[1]
    else:
        assert False, 'Unexpected return value from MessageBox: %s' % (retVal)



'''
def prompt(text='', title='' , default=''):
    """Displays a message box with text input, and OK & Cancel buttons. Returns the text entered, or None if Cancel was clicked."""
    pass

def password(text='', title='', default='', mask='*'):
    """Displays a message box with text input, and OK & Cancel buttons. Typed characters appear as *. Returns the text entered, or None if Cancel was clicked."""
    pass

'''