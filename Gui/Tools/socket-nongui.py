# non-GUI side: connect stream to socket and proceed normally

import sys
import time


if len(sys.argv) > 1:
    from socket_stream_redirect0 import *
    redirectOut()

# non-GUI code
while True:
    print(time.asctime())
    sys.stdout.flush()
    time.sleep(2.0)
