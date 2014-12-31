import os
import shutil
import tempfile

from nose.tools import *

from splicer.functions.filesystem import files, extract_path, decode, contents
from splicer import Relation, Schema

def setup_func():
  global path
  path = tempfile.mkdtemp()


def teardown_func():
  global path
  try:
    shutil.rmtree(path)
  finally:
    path = None


@with_setup(setup_func, teardown_func)
def test_files():
  for artists in range(3):
    for album in range(3):
      album_path = os.path.join(
        path,
        'artist{}/album{}/'.format(artists, album)
      )
      os.makedirs(album_path)

      for track in range(4):
        open(os.path.join(album_path,"{}.ogg".format(track)), 'w')

  songs = files({}, path)

  items = sorted(songs)

  eq_(len(items), 36)

  assert_sequence_equal(
    items,
    [
      ("{}/artist{}/album{}/{}.ogg".format(path, artist,album,track),)
      for artist in range(3)
      for album in range(3)
      for track in range(4)
    ]
  )


from splicer.path import pattern_regex
def test_extract_path():
  r = Relation(
    None, None, #adapter, name, note needed for test
    Schema([dict(type="STRING", name="path")]),
    lambda ctx: iter((
      ('/Music/Nirvana/Nevermind/Smells Like Teen Spirit.ogg',),
      ('/Videos/Electric Boogaloo.mp4',)
    ))
  )


  assert_sequence_equal(
    list(extract_path({}, r, "/Music/{artist}/{album}/{track}.{ext}")),
    [
      (
        '/Music/Nirvana/Nevermind/Smells Like Teen Spirit.ogg', 
        'Nirvana',
        'Nevermind', 
        'Smells Like Teen Spirit',
        'ogg'
      )
    ]
  )

@with_setup(setup_func, teardown_func)
def test_contents():
  p = os.path.join(path, 'test.csv')
  open(p,'w').write('field1,field2\n1,2\n')

  r = Relation(
    None, None,
    Schema([dict(type="STRING", name="path")]), 
    lambda ctx: iter((
      (p,),
    ))
  )
  

  assert_sequence_equal(
    list(contents({}, r,  'path')),
    [
      (p, 'field1,field2\n1,2\n')
    ]
  )

@with_setup(setup_func, teardown_func)
def test_decode():
  p = os.path.join(path, 'test.csv')
  open(p,'w').write('field1,field2\n1,2\n')


  r = Relation(
    None, None,
    Schema([dict(type="STRING", name="path")]),
    lambda ctx: iter((
      (p,),
    ))
  )

  assert_sequence_equal(
    list(decode({}, r, 0, 'auto')),
    [
      (p, '1', '2')
    ]
  )