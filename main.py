import mfrc522
import utime # ignore: type

def uidToString(uid):
    mystring = ""
    for i in uid:
        mystring = "%02X" % i + mystring
    return mystring

def status_is_ok(status):
    return status == 0

def status_is_err(status):
    return status == 2

def bytearray_to_str(bytearray: list) -> str:
    return ''.join([chr(b) for b in bytearray])

def str_to_bytearray(s: str) -> list:
    return list(bytes(s, 'ascii'))

def handle_non_ok_status(status, error = None):
    if status_is_err(status):
        raise Exception("Error: %s" % error)
    elif status != 0:
        raise Exception("Unknown status %d" % status)


def read(reader: mfrc522.MFRC522, uid: list) -> str:
    FIRST_BLOCK = 0
    BLOCK_COUNT = 64
    
    data = []
    for sector_index in range(FIRST_BLOCK, BLOCK_COUNT):
        if sector_index % 4 == 3:
            # Skip acces blocks
            continue

        status = reader.authKeys(uid, sector_index, [255,255,255,255,255,255], None)
        if not status_is_ok(status):
            raise Exception("Error authenticating sector %d" % sector_index)

        status, block = reader.read(sector_index)
        if status_is_ok(status):
            data.extend(block)
        elif status_is_err(status):
            raise Exception("Error reading block %d" % sector_index)
        else:
            raise Exception("Unknown status %d" % status)
    return bytearray_to_str(data)

reader = mfrc522.MFRC522(sck="GP18", mosi="GP19", miso="GP16", rst="GP17", cs="GP20")
previous_uid = None

try:
    while True:
        reader.init()
        
        status, tag_type = reader.request(reader.REQIDL)
        if not status_is_ok(status):
            # no tag there
            previous_uid = None
            continue
        
        status, uid = reader.SelectTagSN()
        if not status_is_ok(status):
            # no tag there
            previous_uid = None
            continue
        
        if previous_uid == uid:
            continue
        
        if reader.IsNTAG():
            print("NTAG not supported")
            continue
        
        status, tag_type = reader.request(reader.REQIDL)
        if not status_is_ok(status):
            print("Error requesting tag")
            continue

        status, uid2 = reader.SelectTagSN()
        if not status_is_ok(status):
            continue

        if uid != uid2:
            print("Error: UID mismatch")
            continue

        print("UID: %s" % uidToString(uid))
        previous_uid = uid
        try:
            data = read(reader, uid)
            print("Data: %s" % data)
        except Exception as e:
            print("Error reading data: %s" % e)
            # raise e
except KeyboardInterrupt:
    print('bye.')
    
