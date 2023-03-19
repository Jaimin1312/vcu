POLYNOMIAL = 0x741B8CD7
BITS = 32
INITIAL_VALUE = 0xffffffff

def _table_initial_remainder(value):
    return value << (BITS - 8)


def _calculate_remainder(remainder, bit=0):
    if bit < 8:
        return _calculate_remainder(_mod_shift(remainder), bit+1)
    return remainder


def _mod_shift(value):
    if value & (1 << (BITS - 1)):
        return ((value << 1) ^ POLYNOMIAL) & 0xffffffff
    return (value << 1) & 0xffffffff


def _table_entry(value):
    return _calculate_remainder(_table_initial_remainder(value))


_TABLE = tuple(map(_table_entry, range(256)))


def crc(byte_list):
    accumulator = INITIAL_VALUE
    for byte in byte_list:
        accumulator = ((accumulator << 8) ^ _TABLE[ ((accumulator >> (BITS - 8)) ^ byte) &0xff ]) & 0xffffffff
    return accumulator
