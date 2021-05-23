#!/usr/bin/env python
from modules.ShadowSystem import ShadowSystem
import timeit
import hashlib
import argparse
import pickle

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool to encrypt/decrypt files using ShadowSystem symmetric cipher")
    parser.add_argument("files", metavar="files", type=str, nargs="+")
    parser.add_argument("-e", "--encrypt", action="store_true",
                        help="encrypt provided file/files")
    parser.add_argument("-d", "--decrypt", action="store_true",
                        help="decrypt provided file/files")
    args = parser.parse_args()

    shadow_obj = ShadowSystem()
    if args.encrypt and args.decrypt:
        raise Exception("Encrypt and decrypt flags can't be set at the same time.")
    elif not args.encrypt and not args.decrypt:
        raise Exception("Encrypt and decrypt flags can't be both unset.")
    elif args.encrypt:
        for file in args.files:
            current_file = open(file, "rb")
            encrypt_start_time = timeit.default_timer()
            key, encrypted_data = shadow_obj.encrypt(current_file.read())
            encrypt_end_time = timeit.default_timer() - encrypt_start_time
            print("Encryption of file %s completed in %fms" % (file, encrypt_end_time))
            current_file.close()

            with open(file + ".shs", "wb") as f:
                f.write(encrypted_data)

            state_collection_name = hashlib.sha256(encrypted_data).hexdigest()
            with open(state_collection_name, "wb") as f:
                f.write(pickle.dumps(key))
    elif args.decrypt:
        for file in args.files:
            encrypted_file = open(file, "rb").read()
            state_collection_name = hashlib.sha256(encrypted_file).hexdigest()
            with open(state_collection_name, "rb") as key_file:
                key = pickle.load(key_file)
            decrypt_start_time = timeit.default_timer()
            decrypted_data = shadow_obj.decrypt(key, encrypted_file)
            decrypt_end_time = timeit.default_timer() - decrypt_start_time
            print("Decryption completed in %fms" % decrypt_end_time)
            with open(file[:-4], "wb") as decrypted_file:
                decrypted_file.write(decrypted_data)
