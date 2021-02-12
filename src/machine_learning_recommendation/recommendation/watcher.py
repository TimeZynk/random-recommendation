import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from datetime import datetime
import logging
import os
from machine_learning_recommendation.machine_learning.model_reader import ModelReader

DELAY_IN_SECONDS = int(os.getenv("DELAY_IN_SECONDS"))


class Watcher(ModelReader):
    def __init__(self):
        super().__init__()
        self.scheduled = False
        self.DELAY_IN_SECONDS = DELAY_IN_SECONDS
        self.observer = None
        self.event_handler = None

    def start(self):
        self.observer = Observer()
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_any_event = self.on_any_event
        self.observer.schedule(self.event_handler, self.models_dir, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def on_any_event(self, event):

        logger = logging.getLogger(__name__)
        # if event.is_directory:
        #     return None
        if event.event_type in ["modified"]:

            if not self.scheduled:
                self.scheduled = True
                logger.warning(
                    f"Received modified event - {event.src_path, event.event_type, threading.currentThread().ident}. Reload of models scheduled at {datetime.now()}, and will execute in about {self.DELAY_IN_SECONDS/3600} hour(s)."
                )
                threading.Timer(self.DELAY_IN_SECONDS, self.reload_models).start()

    def reload_models(self):
        logger = logging.getLogger(__name__)
        logger.warning(f"Reload of models will now be executed at {datetime.now()}.")
        self.reload_all()
        self.scheduled = False
