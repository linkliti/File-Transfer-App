"""File Transfer App
Usage:
    FTA [-g]
    FTA [--server|--client]
    FTA [-h|--help]
    FTA [-s|--scan]

Options:
    -h --help               Show help
    -g --gui                Graphical user interface
    --server                Launch server
    --client                Launch client scanner
"""
from FTA import init
import docopt

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    if args['--gui'] is False:
        print(args)
        init.text_mode(args)
    else:
        init.window_mode()
