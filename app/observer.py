from datetime import datetime

class Observer:
    def update(self, event, data):
        raise NotImplementedError("Subclasses devem implementar o método update.")

class Logger(Observer):
    def update(self, event, data):
        with open("system.log", "a") as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"{timestamp} - {event}: {data}\n")

class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, event, data):
        for observer in self._observers:
            observer.update(event, data)
