# ----------------------------------------------------------------------------
# General configurations
# comment out any setting in this section to accept Tk or program defaults;
# can also change font/colors from GUI menus, and resize window when open;
# imported via search path: can define per client app, skipped if not on path;
# ----------------------------------------------------------------------------

# initial font
font = ('courier', 9, 'normal')  # family, size, style

# initial color
bg = 'lightcyan'  # colorname or RGB hexstr, eg. '#690f96'
fg = 'black'

# initial size
height = 20  # Tk default: 24 lines
width = 80  # Tk default: 80 characters

# search case-insensitive
caseinsens = True

# ----------------------------------------------------------------------------
# 2.1: Unicode encoding behavior and names for file opens and saves;
# attempts the cases listed below in the order show, until the first one
# that works; set all variables to false/empty/0 to use your platform's
# default (which is 'utf-8' on Windows, or 'ascii' or 'latin-1' on others like
# Unix); savesUseKnownEncoding: 0=No, 1=Yes, for Save only, 2=Yes for Save and
# SaveAs; imported from this file always: sys.path if main, else package
# relative;
# ----------------------------------------------------------------------------

# 1) First try internally known type (eg, email charset)
opensAskUser = True  # 2) If True, try user input (prefill with defaults)
opensEncoding = ''  # 3) If nonempty, try this encoding next
# 4) Then try sys.getdefaultencoding() platform default
# 5) Finally use binary mode bytes and Tk policy as last resort

savesUseKnownEncoding = 1  # 1) If > 0, try known encoding from last open/save
savesAskUser = True  # 2) If True, try user input
savesEncoding = ''  # 3) If nonempty, try this encoding next
# 4) Finally, try sys.getdefaultencoding() as last resort
