# These functions use the operating system's native message box calls.

import sys

# default back to the original functions if no native functions exist.
import pymsgbox
alert = pymsgbox.alert
confirm = pymsgbox.confirm
prompt = pymsgbox.prompt
password = pymsgbox.password


# The platformModule is where we reference the platform-specific functions.
if sys.platform.startswith('java'):
    import pymsgbox._native_java as platformModule
elif sys.platform == 'darwin':
    import pymsgbox._native_osx as platformModule
elif sys.platform == 'win32':
    import pymsgbox._native_win as platformModule
    alert = platformModule.alert
    confirm = platformModule.confirm
else:
    import pymsgbox._native_x11 as platformModule

platformModule # this line used to silence the linting tool. Will be removed once implementation is done


