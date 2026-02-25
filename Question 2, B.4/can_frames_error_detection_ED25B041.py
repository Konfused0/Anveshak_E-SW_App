import csv

POLY=0x4599
CRC_BITS=15
CRC_MASK = (1 << CRC_BITS) - 1

def hex_to_bits(hex_string):
    bits=[]
    for h in hex_string.strip().split():
        byte=int(h,16)
        for i in range(7,-1,-1):
            bits.append((byte >> i) & 1)
    
    return bits


def is_valid_id(id_hex):
    try:
        val = int (id_hex, 16)  
    except ValueError:
        return False
    return 0x000 <= val <= 0x7FF


def is_valid_dlc(dlc):
    return 0<=dlc<=8

def data_len_matches_dlc(data_hex, dlc):
    return len(data_hex.strip().split()) == dlc

def frame_bytes_to_bits(id_hex, dlc, data_hex):
    bits = [0]
    
    id_val = int(id_hex, 16)
    for i in range(10, -1, -1):
        bits.append((id_val >> i) & 1)
    
    bits.extend([0, 0, 0])
    dlc_val = dlc & 0xF
    for i in range(3, -1, -1):
        bits.append((dlc_val >> i) & 1)
    
    bits.extend(hex_to_bits(data_hex))
    return bits

def calculate_crc(bits):
    crc = 0x0000
    for bit in bits:
        crc <<= 1
        msb= (crc>> 14) &1
        crc = ((crc<<1)|bit) & CRC_MASK
        if msb:
            crc ^= POLY
    return crc


def validate_row(row):

    id_hex = row['id'].strip()
    if not is_valid_id(id_hex):
        given_err=row.get('errors', 'none').strip().lower()
        print(f"The CAN frame check is failure (error: bad id). The given error is {given_err}")
        return
    
    try:
        dlc = int(row['dlc'])
        if not is_valid_dlc(dlc):
            given_err=row.get('errors', 'none').strip().lower()
            print(f"The CAN frame check is failure (error: bad dlc). The given error is {given_err}")
            return
    except :
        given_err = row.get('errors', 'none').strip().lower()
        print(f"The CAN frame check is failure (error: bad dlc). The given error is {given_err}")
        return
    
    data_hex = row['data']
    if not data_len_matches_dlc(data_hex, dlc):
        given_err = row.get('errors', 'none').strip().lower()
        print(f"The CAN frame check is failure (error: data length mismatch). The given error is {given_err}")
        return
    
    provided_crc_hex = row.get('crc', '').strip()
    if provided_crc_hex:
        try:
            bits = frame_bytes_to_bits(id_hex, dlc, data_hex)
            computed_crc = calculate_crc(bits)
            provided_crc = int(provided_crc_hex, 16) & CRC_MASK
            if computed_crc != provided_crc:
                given_err = row.get('errors', 'none').strip().lower()
                print(f"The CAN frame check is failure (error: bad crc). The given error is {given_err}")
                return
        except:
            given_err = row.get('errors', 'none').strip().lower()
            print(f"The CAN frame check is failure (error: bad crc). The given error is {given_err}")
            return
        
    given_err = row.get('errors', 'none').strip().lower()
    print(f"The CAN frame check is success (error: none). The given error is {given_err}")

with open('can_frames.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row_num, row in enumerate(reader, start=2):
        validate_row(row)