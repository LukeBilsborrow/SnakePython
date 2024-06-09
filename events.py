import pygame
from collections import defaultdict


class EventHandler:
    events = defaultdict(list)

    def update(self):
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if event.key in self.events:
                    for handler in self.events[event.key]:
                        handler()

            if event.type in self.events:
                for handler in self.events[event.type]:
                    handler()

            else:
                # print(f"Event {event.type} not handled")
                pass

    def add_handler(self, event_type, handler):
        self.events[event_type].append(handler)
