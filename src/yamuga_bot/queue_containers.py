from src.yamuga_bot.yandex_handler import TrackContainer


class ContainersQueue(object):
    def __init__(self):
        self.queue: [TrackContainer] = []
        self.container_number = 0

    def append_container(self, container: TrackContainer):
        self.queue.append(container)

    def clear(self):
        self.container_number = 0
        self.queue.clear()

    def next_track(self) -> (str, str):
        if self.container_number == len(self.queue):
            return None
        track = self.queue[self.container_number].next_track()
        if track is None:
            self.container_number += 1
            return self.next_track()
        return track

    def prev_track(self) -> (str, str):
        if self.queue[self.container_number] is None:
            return None
        track = self.queue[self.container_number].prev_track()
        if track is None:
            if self.container_number == 0:
                return None
            self.container_number -= 1
            if self.queue[self.container_number] is None:
                return None
            track = self.queue[self.container_number].last_track()
            if track is None:
                return None
        return track
