"""File Transfer App
Usage:
    FTA [-t=TYPE]
    FTA -h | --help

Options:
    -h --help           Show this screen
    -t=<gui|text>       Change type [default: gui]
"""
from FTA import init
import docopt

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    mode = args['-t']
    if mode == 'text':
        init.text_mode()
    elif mode == 'gui':
        init.window_mode()
