import signal
import threading
import sys

class GracefulShutdown:
    def __init__(self):
        self.shutdown_requested = False
        self._lock = threading.Lock()

    def trigger(self):
        with self._lock:
            if self.shutdown_requested:
                return
            self.shutdown_requested = True
            print("Graceful shutdown initiated: stopping processing, saving state, closing providers")
            # You can also do actual cleanup here: close DB, flush logs, save wallet snapshot, etc.

    def is_requested(self) -> bool:
        return self.shutdown_requested
