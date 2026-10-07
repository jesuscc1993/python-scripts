import os
import tempfile
import pytest

from .. import Attr

@pytest.fixture
def temp_file():
  '''Create a temporary file for testing.'''
  with tempfile.NamedTemporaryFile(delete=False) as f:
    temp_path = f.name
  yield temp_path
  if os.path.exists(temp_path):
    try:
      Attr.remove(temp_path, ['h', 's', 'r'])
      os.remove(temp_path)
    except:
      pass

class TestAttrAdd:

  def test_add_hidden_attribute(self, temp_file):
    Attr.add(temp_file, ['h'])
    assert Attr.has(temp_file, 'h')

  def test_add_system_attribute(self, temp_file):
    Attr.add(temp_file, ['s'])
    assert Attr.has(temp_file, 's')

  def test_add_readonly_attribute(self, temp_file):
    Attr.add(temp_file, ['r'])
    assert Attr.has(temp_file, 'r')

  def test_add_multiple_attributes(self, temp_file):
    Attr.add(temp_file, ['h', 's'])
    assert Attr.has(temp_file, 'h')
    assert Attr.has(temp_file, 's')

  def test_add_nonexistent_path(self):
    Attr.add('/nonexistent/path/file.txt', ['h'])

class TestAttrRemove:

  def test_remove_hidden_attribute(self, temp_file):
    Attr.add(temp_file, ['h'])
    assert Attr.has(temp_file, 'h')
    Attr.remove(temp_file, ['h'])
    assert not Attr.has(temp_file, 'h')

  def test_remove_system_attribute(self, temp_file):
    Attr.add(temp_file, ['s'])
    assert Attr.has(temp_file, 's')
    Attr.remove(temp_file, ['s'])
    assert not Attr.has(temp_file, 's')

  def test_remove_readonly_attribute(self, temp_file):
    Attr.add(temp_file, ['r'])
    assert Attr.has(temp_file, 'r')
    Attr.remove(temp_file, ['r'])
    assert not Attr.has(temp_file, 'r')

  def test_remove_multiple_attributes(self, temp_file):
    Attr.add(temp_file, ['h', 's', 'r'])
    Attr.remove(temp_file, ['h', 's'])
    assert not Attr.has(temp_file, 'h')
    assert not Attr.has(temp_file, 's')
    assert Attr.has(temp_file, 'r')

  def test_remove_nonexistent_path(self):
    Attr.remove('/nonexistent/path/file.txt', ['h'])

class TestAttrHas:

  def test_has_hidden_attribute(self, temp_file):
    Attr.add(temp_file, ['h'])
    assert Attr.has(temp_file, 'h')

  def test_has_no_hidden_attribute(self, temp_file):
    assert not Attr.has(temp_file, 'h')

  def test_has_system_attribute(self, temp_file):
    Attr.add(temp_file, ['s'])
    assert Attr.has(temp_file, 's')

  def test_has_readonly_attribute(self, temp_file):
    Attr.add(temp_file, ['r'])
    assert Attr.has(temp_file, 'r')

  def test_has_nonexistent_path(self):
    assert not Attr.has('/nonexistent/path/file.txt', 'h')

class TestAttrToggle:

  def test_toggle_add_hidden(self, temp_file):
    assert not Attr.has(temp_file, 'h')
    Attr.toggle(temp_file, 'h')
    assert Attr.has(temp_file, 'h')

  def test_toggle_remove_hidden(self, temp_file):
    Attr.add(temp_file, ['h'])
    assert Attr.has(temp_file, 'h')
    Attr.toggle(temp_file, 'h')
    assert not Attr.has(temp_file, 'h')

  def test_toggle_system(self, temp_file):
    assert not Attr.has(temp_file, 's')
    Attr.toggle_system(temp_file)
    assert Attr.has(temp_file, 's')
    Attr.toggle_system(temp_file)
    assert not Attr.has(temp_file, 's')

  def test_toggle_nonexistent_path(self):
    Attr.toggle('/nonexistent/path/file.txt', 'h')

class TestAttrSet:

  def test_set_multiple_attributes(self, temp_file):
    Attr.set(temp_file, ['h', 's'], True)
    assert Attr.has(temp_file, 'h')
    assert Attr.has(temp_file, 's')
    Attr.set(temp_file, ['h', 's'], False)
    assert not Attr.has(temp_file, 'h')
    assert not Attr.has(temp_file, 's')

  def test_set_nonexistent_path(self):
    Attr.set('/nonexistent/path/file.txt', ['h'], True)

class TestAttrSetFlags:

  def test_set_hidden(self, temp_file):
    Attr.set_hidden(temp_file, True)
    assert Attr.is_hidden(temp_file)
    Attr.set_hidden(temp_file, False)
    assert not Attr.is_hidden(temp_file)

  def test_set_system(self, temp_file):
    Attr.set_system(temp_file, True)
    assert Attr.is_system(temp_file)
    Attr.set_system(temp_file, False)
    assert not Attr.is_system(temp_file)

  def test_set_readonly(self, temp_file):
    Attr.set_readonly(temp_file, True)
    assert Attr.is_readonly(temp_file)
    Attr.set_readonly(temp_file, False)
    assert not Attr.is_readonly(temp_file)

class TestAttrIsHidden:

  def test_is_hidden_true(self, temp_file):
    Attr.add(temp_file, ['h'])
    assert Attr.is_hidden(temp_file)

  def test_is_hidden_false(self, temp_file):
    assert not Attr.is_hidden(temp_file)

  def test_is_hidden_nonexistent_path(self):
    assert not Attr.is_hidden('/nonexistent/path/file.txt')

class TestAttrHideShow:

  def test_hide_file(self, temp_file):
    Attr.hide(temp_file)
    assert Attr.has(temp_file, 'h')

  def test_show_file(self, temp_file):
    Attr.hide(temp_file)
    assert Attr.has(temp_file, 'h')
    Attr.show(temp_file)
    assert not Attr.has(temp_file, 'h')

  def test_hide_with_multiple_attrs(self, temp_file):
    Attr.hide(temp_file, ['h', 's'])
    assert Attr.has(temp_file, 'h')
    assert Attr.has(temp_file, 's')

  def test_show_with_multiple_attrs(self, temp_file):
    Attr.hide(temp_file, ['h', 's', 'r'])
    Attr.show(temp_file, ['h', 's'])
    assert not Attr.has(temp_file, 'h')
    assert not Attr.has(temp_file, 's')
    assert Attr.has(temp_file, 'r')
