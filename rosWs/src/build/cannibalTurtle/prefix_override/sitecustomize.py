import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/media/ashwin-k/ashwinStorage/1.insti/cfi/guild/aero/rosWs/src/install/cannibalTurtle'
