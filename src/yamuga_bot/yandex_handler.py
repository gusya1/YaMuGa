from yandex_music.client import Client
from yandex_music import Album, Playlist, Track
from typing import Union, Optional

login_parameters = ("", "")


class TrackContainer(object):

    def __init__(self, container: Union[Album, Playlist, Track]):
        self.container = container
        self.current_number = None
        if isinstance(self.container, Album):
            self.current_number = [0, -1]
        if isinstance(self.container, Playlist):
            self.current_number = -1
        if isinstance(self.container, Track):
            self.current_number = 0

    # def get_current_track(self) -> (str, str):
    #     if isinstance(self.container, Album):
    #         vol_num, track_num = self.current_number
    #         if vol_num >= len(self.container.volumes):
    #             return None
    #         vol = self.container.volumes[vol_num]
    #         if track_num >= len(vol):
    #             return None
    #         return self.__get_track_info(vol[track_num])
    #     if isinstance(self.container, Playlist):
    #         if self.current_number >= len(self.container.tracks):
    #             return None
    #         track = self.container.tracks[self.current_number].track
    #         return self.__get_track_info(track)
    #     if isinstance(self.container, Track):
    #         if self.current_number != 0:
    #             return None
    #         return self.__get_track_info(self.container)

    def next_track(self) -> (str, str):
        if isinstance(self.container, Album):
            vol_num, track_num = self.current_number
            if track_num + 1 == len(self.container.volumes[vol_num]):
                self.current_number[1] = 0
                if vol_num + 1 == len(self.container.volumes):
                    return None
                self.current_number[0] += 1
            else:
                self.current_number[1] += 1
            track = self.container.volumes[self.current_number[0]][self.current_number[1]]
            return self.__get_track_info(track)
        if isinstance(self.container, Playlist):
            if self.current_number + 1 == len(self.container.tracks):
                return None
            self.current_number += 1
            track = self.container.tracks[self.current_number].track
            return self.__get_track_info(track)
        if isinstance(self.container, Track):
            if self.current_number == 0:
                self.current_number += 1
                return self.__get_track_info(self.container)
            return None

    def prev_track(self) -> (str, str):
        if isinstance(self.container, Album):
            vol_num, track_num = self.current_number
            if track_num == 0:
                if vol_num == 0:
                    return None
                self.current_number[0] -= 1
                self.current_number[1] = len(self.container.volumes[self.current_number[0]]) - 1
            else:
                self.current_number[1] -= 1
            track = self.container.volumes[self.current_number[0]][self.current_number[1]]
            return self.__get_track_info(track)
        if isinstance(self.container, Playlist):
            if self.current_number == 0:
                return None
            self.current_number -= 1
            track = self.container.tracks[self.current_number].track
            return self.__get_track_info(track)
        if isinstance(self.container, Track):
            self.current_number = -1
            return None

    def last_track(self) -> (str, str):
        if isinstance(self.container, Album):
            vol_num = len(self.container.volumes) - 1
            track_num = len(self.container.volumes[vol_num]) - 1
            self.current_number = [vol_num, track_num]
            track = self.container.volumes[vol_num][track_num]
            return self.__get_track_info(track)
        if isinstance(self.container, Playlist):
            self.current_number = len(self.container.tracks) - 1
            track = self.container.tracks[self.current_number].track
            return self.__get_track_info(track)
        if isinstance(self.container, Track):
            if self.current_number == 0:
                self.current_number += 1
                return self.__get_track_info(self.container)
            return None

    def first_track(self) -> (str, str):
        if isinstance(self.container, Album):
            self.current_number = [0, -1]
        if isinstance(self.container, Playlist):
            self.current_number = -1
        if isinstance(self.container, Track):
            self.current_number = 0
        return self.next_track()

    # TODO сделать функцию first_track

    def __get_track_info(self, track: Track) -> (str, str):
        list_of_di = track.getDownloadInfo(True)
        info_string = "%s -- %s -- %s " % (track.title, track.artists[0].name, track.albums[0].title)
        link = None
        # TODO поэксперементировать с битрейтом


        for info in list_of_di:
            # if info.codec == "mp3" and info.bitrate_in_kbps == 192:
            if info.codec == "aac":
                link = info.getDirectLink()
                break
        print(link)
        return info_string, link


def _init_client(token):
    client = Client(token)
    client.init()
    return client


class YandexDriver(object):

    def __init__(self, token):
        self.client = _init_client(token)
        self.queueStatus = False
        self.container: Union[Album, Playlist]
        self.current_number: [int, int] | int


    def get_track_from_search(self, reqest) -> Optional[TrackContainer]:
        search_result = self.client.search(reqest, type_="track")
        track = search_result.tracks.results[0]
        if track is None:
            return None
        return TrackContainer(track)

    def get_album_from_link(self, url) -> Optional[TrackContainer]:
        if url[:30:] != "https://music.yandex.ru/album/":
            return None
        number = url[30::]
        album = self.client.albumsWithTracks(number)
        if album is None:
            return None
        return TrackContainer(album)

    def get_playlist_from_link(self, url : str) -> Optional[TrackContainer]:
        """https://music.yandex.ru/users/yamusic-trending/playlists/1000"""
        correct_parts = ("https:", "", "music.yandex.ru", "users", None, "playlists", None)
        parts = url.split("/")

        if len(correct_parts) != len(parts):
            return None
        for i in range(len(correct_parts)):
            if correct_parts[i] is None:
                continue
            if correct_parts[i] != parts[i]:
                return None

        playlist = self.client.usersPlaylists(parts[6], parts[4])
        if playlist is None:
            return None
        return TrackContainer(playlist[0])

    def __resetQueue(self):
        self.container = None
        self.current_number = 0
        self.queueStatus = False
