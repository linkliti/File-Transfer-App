from threading import Thread, Lock
from time import perf_counter
from time import sleep
import socket


class Threader:
    """Class that calls a list of functions in a limited number of
    threads."""

    def __init__(self, threads=30):
        self.thread_lock = Lock()
        self.functions_lock = Lock()
        self.functions = []
        self.threads = []
        self.nthreads = threads
        self.running = True
        self.print_lock = Lock()
        socket.setdefaulttimeout(0.1)

    def stop(self) -> None:
        """Signal all worker threads to stop"""
        self.running = False

    def append(self, function, *args) -> None:
        """Add the function to a list of functions to be run"""
        self.functions.append((function, args))

    def start(self) -> None:
        """Create a limited number of threads"""
        for i in range(self.nthreads):
            thread = Thread(target=self.worker, daemon=True)
            # We need to pass in `thread` as a parameter so we
            # have to use `<threading.Thread>._args` like this:
            thread._args = (thread, )
            self.threads.append(thread)
            thread.start()

    def join(self) -> None:
        """Joins the threads one by one until all of them are done."""
        for thread in self.threads:
            thread.join()

    def worker(self, thread: Thread) -> None:
        """Functions list worker"""
        while self.running and (len(self.functions) > 0):
            # Get a function
            with self.functions_lock:
                function, args = self.functions.pop(0)
            # Call that function
            function(*args)

        # Remove the thread from the list of threads.
        with self.thread_lock:
            self.threads.remove(thread)


def connect(hostname, port):
    """IP Scanner"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((hostname, port))
        with threader.print_lock:
            if result == 0:
                print(f"Found {hostname}\n")


def ip_list(ip):
    """IP generator for Threader"""
    if ip.count('.') == 3:
        threader.append(connect, ip, port)
    else:
        for i in range(255+1):
            ip_list(ip + f'.{i}')


def main(ips, port_num) -> int:
    """Client main function"""
    # Add IPs to scanner
    global threader
    global port
    port = port_num
    for ip in ips:
        threader = Threader(10)
        ip_list(ip)
        threader.start()
        threader.join()
        print(f"Done searching {ip}")
    return 0


if __name__ == '__main__':
    main()
