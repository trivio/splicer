from datetime import date
from nose.tools import *

from splicer import Query, Schema, Field
from splicer.servers.file_server import FileServer

import os
import tempfile
import shutil

def setup_func():
  global path
  path = tempfile.mkdtemp()


def teardown_func():
  global path
  try:
    shutil.rmtree(path)
  finally:
    path =None


@with_setup(setup_func, teardown_func)
def test_file_server_with_schemas():
  for artists in range(3):
    for album in range(3):
      album_path = os.path.join(
        path,
        'artist{}/album{}/'.format(artists, album)
      )
      os.makedirs(album_path)

      for track in range(4):
        open(os.path.join(album_path,"{}.ogg".format(track)), 'w')

  
  server = FileServer(
    songs = dict(
      root_dir = path,
      pattern = "{artist}/{album}/{track}.{ext}",
      content_column="content",
    )
  )


  songs = server.get_relation('songs')
  assert_sequence_equal(
    songs.schema.fields,
    [
      Field(name="artist", type="STRING"),
      Field(name="album", type="STRING"),
      Field(name="track", type="STRING"),
      Field(name="ext", type="STRING"),
      Field(name="content", type="BINARY")
    ]
  )

  assert_sequence_equal(
    list(songs),
    [
      ("artist{}".format(artist), 'album{}'.format(album), str(track), 'ogg', '')
      for artist in range(3)
      for album in range(3)
      for track in range(4)
    ]
  )

@with_setup(setup_func, teardown_func)
def test_file_server_with_deserializing():
  os.makedirs(os.path.join(path, 'alternative'))
  open(
    os.path.join(path, "alternative/data.csv"),
    'w'
  ).write(
    "artist,album,track_number,track_name\n"
    'Nirvana,nevermind,1,"Smells Like Teen Spirit"\n'
    'They Might Be Giants,Flood,7,Partical Man\n'
  )
  
  # files that don't match the pattern should be ignored
  open(
    os.path.join(path, "alternative/random.ogg"),
    'w'
  ).write('')


  server = FileServer(
    songs = dict(
      root_dir = path,
      pattern = "{genre}/data.csv",
      decode="text/csv"
    )
  )

  songs = server.get_relation('songs')

  assert_sequence_equal(
    songs.schema.fields,
    [
      Field(name="genre", type="STRING"),
      Field(name="artist", type="STRING"),
      Field(name="album", type="STRING"),
      Field(name="track_number", type="STRING"),
      Field(name="track_name", type="STRING")
    ]
  )

  assert_sequence_equal(
    list(songs),
    [
      ('alternative', 'Nirvana', 'nevermind', '1', 'Smells Like Teen Spirit'),
      ('alternative', 'They Might Be Giants', 'Flood', '7', 'Partical Man')
    ]  
  )