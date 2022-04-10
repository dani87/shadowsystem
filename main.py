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
    key = shadow_obj.set_cipher_states()
    if args.encrypt and args.decrypt:
        raise Exception("Encrypt and decrypt flags can't be set at the same time.")
    elif not args.encrypt and not args.decrypt:
        raise Exception("Encrypt and decrypt flags can't be both unset.")
    elif args.encrypt:
        for file in args.files:
            encrypt_start_time = timeit.default_timer()
            with open(file, "rb") as in_file, open(file + ".shs", "wb") as out_file:
                buffer = in_file.read(2048)
                while buffer:
                    encrypted_data_block = shadow_obj.encrypt_block(buffer)
                    out_file.write(encrypted_data_block)
                    buffer = in_file.read(2048)
            encrypt_end_time = timeit.default_timer() - encrypt_start_time
            print("Encryption of file %s completed in %fs" % (file, encrypt_end_time))

            state_collection_name = hashlib.sha256(open(file + ".shs", "rb").read()).hexdigest()
            with open(state_collection_name, "wb") as f:
                f.write(pickle.dumps(key))
    elif args.decrypt:
        for file in args.files:
            state_collection_name = hashlib.sha256(open(file, "rb").read()).hexdigest()
            with open(state_collection_name, "rb") as key_file:
                key = pickle.load(key_file)

            decrypt_start_time = timeit.default_timer()
            with open(file, "rb") as in_file, open(file[:-4], "wb") as out_file:
                buffer = in_file.read(2048)
                while buffer:
                    decrypted_data_block = shadow_obj.decrypt_block(key, buffer)
                    out_file.write(decrypted_data_block)
                    buffer = in_file.read(2048)
            decrypt_end_time = timeit.default_timer() - decrypt_start_time
            print("Decryption of file %s completed in %fs" % (file, decrypt_end_time))

