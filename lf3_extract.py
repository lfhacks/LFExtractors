from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os, tarfile, io, sys

KEY = b'\x44\xee\x33\x41\x4a\x56\x48\xe1\x5e\x1c\x7e\x15\x85\xb1\x07\x38'

def decrypt_lf3(path):
    with open(path, 'rb') as f:
        # read the IV (stored in the first 16 bytes)
        IV = f.read(16)

        # create a cipher using AES with our key, a CTR with our IV and the default backend
        cipher = Cipher(algorithms.AES(KEY), modes.CTR(IV), backend=default_backend())

        # read the encrypted data
        encrypted = f.read()

        # decrypt the data
        decrypter = cipher.decryptor()
        decrypted = decrypter.update(encrypted) + decrypter.finalize()

    # return the data
    return decrypted

def extract_lf3(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    
    print('Decrypting...')
    tar_data = decrypt_lf3(path)

    print('Writing...')
    if not os.path.exists(filename):
        os.makedirs(filename)

    with tarfile.open(fileobj=io.BytesIO(tar_data)) as tar:
        tar.extractall(filename)

def main():
    if len(sys.argv) == 1:
        path = input(str('Enter the path to the LF3 file: '))
    else:
        path = sys.argv[1]
        
    extract_lf3(path)

if __name__ == '__main__':
    main()
        
    
