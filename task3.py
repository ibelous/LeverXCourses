from threading import Lock
from concurrent.futures import ThreadPoolExecutor
a = 0


def function(arg, lock: Lock):
    global a
    for _ in range(arg):
        with lock:
            a += 1


def main():
    threads = []
    lock = Lock()
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(5):
            threads.append(executor.submit(function(1000000, lock, )))
    print("----------------------", a)  # ???


main()
