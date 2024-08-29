from dataclasses import dataclass
import struct
import array
import sys

CBF_MAGIC = 0x9ABCDEF0

@dataclass
class CBF:
    # Summary
    magic_num:   int = 0        # 4 bytes
    cbf_version: int = 0        # 4 bytes
    kernel_load: int = 0        # 4 bytes
    kernel_jump: int = 0        # 4 bytes
    kernel_size: int = 0        # 4 bytes
    crc_check:   int = 0        # 4 bytes

    # Kernel image
    kernel_img:  bytes = b''    # kernel_size bytes
    kernel_crc:  int = 0        # 4 bytes
    padding:     bytes = b''    # until EOF (I don't read this data)

def unpack_uint(data):
    return int.from_bytes(data, "little") # little endian

# This is from OpenLFConnect
def lf_crc(data):
    a = array.array('I', data)
    crc = 0

    for c in a:
        crc = 1 + (crc ^ c)

    return crc

def read_cbf(file_path):
    cbf_data = CBF()
    with open(file_path, 'rb') as f:
        # Summary (the end bytes are shifted by 1 and I dont know why)
        summary = f.read(20)
        cbf_data.magic_num = unpack_uint(summary[0:4])
        cbf_data.cbf_version = unpack_uint(summary[4:8])
        cbf_data.kernel_load = unpack_uint(summary[8:12])
        cbf_data.kernel_jump = unpack_uint(summary[12:16])
        cbf_data.kernel_size = unpack_uint(summary[16:20])
        
        # CRC checksum of summary
        cbf_data.crc_check = unpack_uint(f.read(4))

        # Kernel image
        cbf_data.kernel_img = f.read(cbf_data.kernel_size) # read until kernel size finished
        cbf_data.kernel_crc = unpack_uint(f.read(4))

    # Check CBF magic
    if cbf_data.magic_num != CBF_MAGIC:
        print('Not a CBF file!')
        return
    
    # Check summary CRC
    scrc = lf_crc(summary)
    if scrc != cbf_data.crc_check:
        print(f'Summary CRC is not equal to the CBF\'s CRC!\nExpected: {hex(cbf_data.crc_check)}, Got: {hex(scrc)}')
        return

    # Check kernel CRC
    kcrc = lf_crc(cbf_data.kernel_img)
    if kcrc != cbf_data.kernel_crc:
        print(f'Kernel CRC is not equal to the CBF\'s CRC!\nExpected: {hex(cbf_data.kernel_crc)}, Got: {hex(kcrc)}')
        return
    
    return cbf_data

def main():
    if len(sys.argv) == 1:
        path = input(str('Enter the path to the CBF file: '))
    else:
        path = sys.argv[1]
        
    cbf = read_cbf(path)

    if cbf != None:
        with open('Image', 'wb') as f:
            f.write(cbf.kernel_img)
            print('Written!')

if __name__ == '__main__':
    main()
