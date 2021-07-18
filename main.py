#!/usr/bin/env python
from modules.ShadowSystem import ShadowSystem
import timeit
import hashlib
import argparse
import pickle
import os
import concurrent.futures

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool to encrypt/decrypt files using ShadowSystem symmetric cipher")
    parser.add_argument("files", metavar="files", type=str, nargs="+")
    parser.add_argument("-e", "--encrypt", action="store_true",
                        help="encrypt provided file/files")
    parser.add_argument("-d", "--decrypt", action="store_true",
                        help="decrypt provided file/files")
    args = parser.parse_args()

    BLOCK_SIZE = 4096
    shadow_obj = ShadowSystem()
    if args.encrypt and args.decrypt:
        raise Exception("Encrypt and decrypt flags can't be set at the same time.")
    elif not args.encrypt and not args.decrypt:
        raise Exception("Encrypt and decrypt flags can't be both unset.")
    elif args.encrypt:
        for file in args.files:
            states = []
            futures = []
            current_file = open(file, "rb")
            encrypted_file = open(file + ".shs", "w+b")
            encrypt_start_time = timeit.default_timer()
            current_file_block = current_file.read(BLOCK_SIZE)
            with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                while current_file_block:
                    futures.append(executor.submit(shadow_obj.encrypt, current_file_block))
                    current_file_block = current_file.read(BLOCK_SIZE)
            for future in futures:
                key, encrypted_data = future.result()
                encrypted_file.write(encrypted_data)
                states.append(key)
            encrypt_end_time = timeit.default_timer() - encrypt_start_time
            print("Encryption of file %s completed in %fms" % (file, encrypt_end_time))
            current_file.close()
            encrypted_file.seek(0)
            state_collection_name = hashlib.sha256(encrypted_file.read()).hexdigest()
            encrypted_file.close()
            with open(state_collection_name, "wb") as f:
                f.write(pickle.dumps(states))
    elif args.decrypt:
        for file in args.files:
            futures = []
            encrypted_file = open(file, "rb")
            decrypted_file = open(file[:-4], "wb")
            state_collection_name = hashlib.sha256(encrypted_file.read()).hexdigest()
            with open(state_collection_name, "rb") as key_file:
                states = pickle.load(key_file)
            decrypt_start_time = timeit.default_timer()
            encrypted_file.seek(0)
            encrypted_file_block = encrypted_file.read(BLOCK_SIZE)
            with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                while encrypted_file_block:
                    for state in states:
                        futures.append(executor.submit(shadow_obj.decrypt, state, encrypted_file_block))
                    encrypted_file_block = encrypted_file.read(BLOCK_SIZE)
            for future in futures:
                decrypted_file.write(future.result())
            encrypted_file.close()
            decrypted_file.close()
            decrypt_end_time = timeit.default_timer() - decrypt_start_time
            print("Decryption of file %s completed in %fms" % (file, decrypt_end_time))
