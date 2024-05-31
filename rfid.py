import mfrc522
from util import callback_helper

class RFID:
  FIRST_BLOCK = 4
  BLOCK_COUNT = 64
  DATA_BLOCKS = (BLOCK_COUNT - FIRST_BLOCK) - (BLOCK_COUNT - FIRST_BLOCK) // 4

  DEFAULT_AUTH_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

  on_data_read_start: function | None = None
  '''`Callable[[str], None]`'''
  on_data_read_end: function | None = None
  '''`Callable[[str], None]`'''
  on_data_read_error: function | None = None
  '''`Callable[[Exception], None]`'''
  on_data_write: function | None = None
  '''`Callable[[str], None]`'''
  on_data_write_end: function | None = None
  '''`Callable[[], None]`'''
  on_data_write_error: function | None = None
  '''`Callable[[Exception], None]`'''

  def __init__(self):
    self.reader = mfrc522.MFRC522(sck="GP18", mosi="GP19", miso="GP16", rst="GP17", cs="GP20")
    self.last_uid = None

  def _uidToString(self, uid):
    mystring = ""
    for i in uid:
      mystring = "%02X" % i + mystring
    return mystring

  def _status_is_ok(self, status):
    return status == 0

  def _status_is_err(self, status):
    return status == 2

  def _bytearray_to_str(self, bytearray: list) -> str:
    return ''.join([chr(b) for b in bytearray])

  def _str_to_bytearray(self, s: str) -> list:
    return list(bytes(s, 'ascii'))

  def _handle_non_ok_status(self, status, error = None):
    if self._status_is_err(status):
      raise Exception("Error: %s" % error)
    elif status != 0:
      raise Exception("Unknown status %d" % status)

  def _auth(self, uid: list, sector_index: int) -> bool:
    status = self.reader.auth(self.reader.AUTHENT1A, sector_index, self.DEFAULT_AUTH_KEY, uid)
    self._handle_non_ok_status(status, "Error authenticating sector %d" % sector_index)
    return True

  def _read(self, uid: list) -> str:
    data = []
    for sector_index in range(self.FIRST_BLOCK, self.BLOCK_COUNT):
      if sector_index % 4 == 3:
        # Skip access blocks
        continue
      self._auth(uid, sector_index)
      status, block = self.reader.read(sector_index)
      if self._status_is_ok(status):
        data.extend(block)
      elif self._status_is_err(status):
        raise Exception("Error reading block %d" % sector_index)
      else:
        raise Exception("Unknown status %d" % status)
      if (0 in block):
        break
    data = data[:data.index(0)]
    return self._bytearray_to_str(data)

  def _write(self, uid: list, data: str) -> list:
    encoded_data = self._str_to_bytearray(data)
    encoded_data += [0] * (self.DATA_BLOCKS * 16 - len(encoded_data))
    for sector_index in range(self.FIRST_BLOCK, self.BLOCK_COUNT):
      if sector_index % 4 == 3:
        # Skip access blocks
        continue
      self._auth(uid, sector_index)
      status = self.reader.write(sector_index, encoded_data[:16])
      if self._status_is_ok(status):
        encoded_data = encoded_data[16:]
      elif self._status_is_err(status):
        raise Exception("Error writing block %d" % sector_index)
      else:
        raise Exception("Unknown status %d" % status)
    return encoded_data
  
  def _init_interaction(self) -> list | None:
    self.reader.init()
    status, _ = self.reader.request(self.reader.REQIDL)
    if not self._status_is_ok(status):
      # no tag there
      self.previous_uid = None
      return None
    
    status, uid = self.reader.SelectTagSN()
    if not self._status_is_ok(status):
      # no tag there
      self.previous_uid = None
      return None
    if self.previous_uid == uid:
      return None
    self.previous_uid = uid
    return uid

  def read(self) -> str | None:
    try:
      uid = self._init_interaction()
      if uid is not None:
        callback_helper(self.on_data_read_start, self._uidToString(uid))
        data = self._read(uid)
        callback_helper(self.on_data_read_end, data)
        return data
    except Exception as e:
      callback_helper(self.on_data_read_error, e)
    return None
  
  def write(self, data: str) -> list | None:
    try:
      uid = self._init_interaction()
      if uid is not None:
        callback_helper(self.on_data_write, self._uidToString(uid))
        written_data = self._write(uid, data)
        callback_helper(self.on_data_write_end)
        return written_data
    except Exception as e:
      callback_helper(self.on_data_write_error, e)
      raise e
    return None