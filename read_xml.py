# Created by chris at 04.04.22 21:04
import os
# pylint: disable=unused-import
from pathlib import Path
from typing import Dict, Iterable  # noqa: F401
# pylint: enable=unused-import
import xml.etree.ElementTree as ET

import dataclasses

DEFAULT_PATH = os.getenv('HOME', '') + "/Documents/rekordbox.xml"


@dataclasses.dataclass
class Track:
    TrackID: int
    Name: str
    Artist: str
    Album: str
    Genre: str
    Kind: str
    Size: int
    TotalTime: int
    # DiscNumber: int
    # TrackNumber: int
    Year: int
    AverageBpm: float
    DateAdded: str
    BitRate: int
    SampleRate: int
    Comments: str
    PlayCount: int
    Rating: int
    Tonality: str
    Label: str
    Location: str
    CuePoints: list = dataclasses.field(default_factory=list)


    @classmethod
    def parse(cls, track: ET.Element):
        field_values = {}  # type: Dict[str, object]
        for field in dataclasses.fields(cls):
            field_value = track.get(field.name)
            if field_value is not None:
                field_value = field.type(field_value)
            field_values[field.name] = field_value

        cps = []
        for mark in track.findall('POSITION_MARK'):
            cps.append(CuePoint.parse(mark))
        field_values['CuePoints'] = cps
        return cls(**field_values)  # type: ignore


@dataclasses.dataclass
class CuePoint:
    Name: str = ""
    Type: int = 0
    Start: float = 0
    Num: int = 0
    Red: int = 255
    Green: int = 255
    Blue: int = 255

    @classmethod
    def parse(cls, position_mark: ET.Element):
        field_values = {}
        for field in dataclasses.fields(cls):
            field_value = position_mark.get(field.name)
            if field_value is not None:
                field_value = field.type(field_value)
            field_values[field.name] = field_value
        return cls(**field_values)  # type: ignore


@dataclasses.dataclass
class Folder:
    Name: str
    Type: int
    Count: int
    Folders: list = dataclasses.field(default_factory=list)
    Playlists: list = dataclasses.field(default_factory=list)
    @classmethod
    def parse(cls, rootfolder: ET.Element):
        field_values = {}
        for field in dataclasses.fields(cls):
            field_value = rootfolder.get(field.name)
            if field_value is not None:
                field_value = field.type(field_value)
            field_values[field.name] = field_value

        folders = []
        playlists = []
        for node in rootfolder.findall('NODE'):
            if node.attrib["Type"] == "0":
                folders.append(Folder.parse(node))
            elif node.attrib["Type"] == "1":
                playlists.append(Playlist.parse(node))
        field_values['Folders'] = folders
        field_values['Playlists'] = playlists
        return cls(**field_values)  # type: ignore


@dataclasses.dataclass
class Playlist:
    Name: str
    Type: int
    KeyType: int
    Entries: int
    Tracks: list = dataclasses.field(default_factory=list)
    @classmethod
    def parse(cls, node: ET.Element):
        field_values = {}
        for field in dataclasses.fields(cls):
            field_value = node.get(field.name)
            if field_value is not None:
                field_value = field.type(field_value)
            field_values[field.name] = field_value

        playlist_tracks = []
        for mark in node.findall('TRACK'):
            playlist_tracks.append(mark.attrib["Key"])
        field_values['Tracks'] = playlist_tracks
        return cls(**field_values)  # type: ignore


def parse_dj_playlists(rb_xml: ET.Element) -> Iterable[Playlist]:
    all_playlists = []
    playlists = rb_xml.find("PLAYLISTS")
    if playlists:
        for playlist in playlists:
            all_playlists.append(Folder.parse(playlist))
    return all_playlists

def parse_dj_collection(dj_collection: ET.Element) -> Iterable[Track]:
    collection = []
    tracks = dj_collection.find('COLLECTION')
    if tracks:
        for track in tracks:
            collection.append(Track.parse(track))
    return collection


def parse_xml_file(file_path: str = DEFAULT_PATH) -> Iterable[Track]:
    tree = ET.parse(file_path)
    root = tree.getroot()
    return parse_dj_collection(root)

if __name__ == "__main__":
    XML_PATH = Path("/home/chris/Desktop/220403.xml")
    collection = parse_xml_file(XML_PATH)
    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    playlists = parse_dj_playlists(root)