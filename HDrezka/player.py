from HDrezka.constants import *
from abc import abstractmethod


class Video:
    def __init__(self):
        self.episode = None
        self.season = None
        self.size = None
        self.quality = None
        self.translate = None
        self.subtitle = None

    def create(self):
        pass

    def load(self):
        return self.get_action()

    @abstractmethod
    def get_action(self):
        raise NotImplementedError

    def get_subtitle(self):
        return ACTION_SUBTITLE


class Film(Video):
    def get_action(self):
        return ACTION_FILM


class Serial(Video):
    def get_action(self):
        return ACTION_SEASON
