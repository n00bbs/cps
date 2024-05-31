import json

class AccessControl:
  def __init__(self, uid: str, is_allowed: bool, name: str):
    self._is_allowed: bool = is_allowed
    self._uid: str = uid
    self._name: str = name

  @staticmethod
  def from_record(uid: str, data: str):
    record = json.loads(data)
    return AccessControl(uid, record["is_allowed"], record["name"])
  
  def to_record(self):
    return json.dumps({
      "is_allowed": self._is_allowed,
      "name": self._name
    })
  
  def get_uid(self) -> str:
    return self._uid
  
  def get_name(self) -> str:
    return self._name
  
  def is_allowed(self) -> bool:
    return self._is_allowed