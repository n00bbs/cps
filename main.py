import mfrc522
from machine import I2C, Pin
from lcd_i2c import LCD

FIRST_BLOCK = 4
BLOCK_COUNT = 64
DATA_BLOCKS = (BLOCK_COUNT - FIRST_BLOCK) - (BLOCK_COUNT - FIRST_BLOCK) // 4

DEFAULT_AUTH_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

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

def auth(reader: mfrc522.MFRC522, uid: list, sector_index: int) -> bool:
    status = reader.auth(reader.AUTHENT1A, sector_index, DEFAULT_AUTH_KEY, uid)
    handle_non_ok_status(status, "Error authenticating sector %d" % sector_index)
    return True

def read(reader: mfrc522.MFRC522, uid: list) -> str:
    data = []
    for sector_index in range(FIRST_BLOCK, BLOCK_COUNT):
        if sector_index % 4 == 3:
            # Skip acces blocks
            continue
        auth(reader, uid, sector_index)
        status, block = reader.read(sector_index)
        if status_is_ok(status):
            data.extend(block)
        elif status_is_err(status):
            raise Exception("Error reading block %d" % sector_index)
        else:
            raise Exception("Unknown status %d" % status)
        if (0 in block):
            break
    return bytearray_to_str(data)

def write(reader: mfrc522.MFRC522, uid: list, data: str):
    encoded_data = str_to_bytearray(data)
    encoded_data += [0] * (DATA_BLOCKS * 16 - len(encoded_data))
    for sector_index in range(FIRST_BLOCK, BLOCK_COUNT):
        if sector_index % 4 == 3:
            # Skip acces blocks
            continue
        auth(reader, uid, sector_index)
        status = reader.write(sector_index, encoded_data[:16])
        if status_is_ok(status):
            encoded_data = encoded_data[16:]
        elif status_is_err(status):
            raise Exception("Error writing block %d" % sector_index)
        else:
            raise Exception("Unknown status %d" % status)

# Initialize the I2C bus
SCREEN_I2C_ADDR = 0x27     # DEC 39, HEX 0x27
SCREEN_I2C_NUM_ROWS = 2
SCREEN_I2C_NUM_COLS = 16

screen_i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=800000)
lcd = LCD(i2c=screen_i2c, addr=SCREEN_I2C_ADDR, cols=SCREEN_I2C_NUM_COLS, rows=SCREEN_I2C_NUM_ROWS)

lcd.begin()

# initialize the RFID reader
reader = mfrc522.MFRC522(sck="GP18", mosi="GP19", miso="GP16", rst="GP17", cs="GP20")
previous_uid = None

current_mode = "read"

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

        print("UID: %s" % uidToString(uid))
        previous_uid = uid
        if(current_mode == "read"):
            data = read(reader, uid)
            lcd.clear()
            lcd.print(data)
            print("Data: %s" % data)
        elif(current_mode == "write"):
            data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent."
            write(reader, uid, data)
            print("Data written.")

except KeyboardInterrupt:
    print('bye.')
    
