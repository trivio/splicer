from datetime import date
from nose.tools import *

from splicer import Query, Schema, Field
from splicer.servers.file_server import FileServer

import os
import tempfile
import shutil

def setup(mod):
  mod.path = tempfile.mkdtemp()

  for artists in range(3):
    for album in range(3):
      album_path = os.path.join(
        mod.path,
        'artist{}/album{}/'.format(artists, album)
      )
      os.makedirs(album_path)

      for track in range(4):
        open(os.path.join(album_path,"{}.ogg".format(track)), 'w')


def teardown(mod):
  try:
    shutil.rmtree(mod.path)
  finally:
    mod.path =None



def test_file_server_with_schemas():
  
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