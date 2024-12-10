import os
import secrets
import random


class ShadowSystem:
    def __init__(self, sbox_rounds=10, sbox_shuffle_rounds=6, block_size=16):
        self.sbox_rounds = sbox_rounds
        self.sbox_shuffle_rounds = sbox_shuffle_rounds
        self.block_size = block_size
        self.states = {'sbox_rounds_states': [], 'sbox_shuffle_rounds_states': []}
    @staticmethod
    def read_in_chunks(data, chunk_size=16):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def invert(self, sbox):
        """Create an inverse of the S-box."""
        sboxinv = list(range(256))
        for index, value in enumerate(sbox):
            sboxinv[value] = index
        return sboxinv

    def create(self, state):
        """Generate an S-box based on the given state."""
        sbox = list(range(256))
        for index, number in enumerate(sbox):
            for random_byte in state:
                # Swap bytes in the S-box
                sbox[random_byte], sbox[index] = sbox[index], sbox[random_byte]
        return sbox

    def set_cipher_states(self):
        """Set up cipher states with secure random bytes."""
        for _ in range(self.sbox_rounds):
            self.states['sbox_rounds_states'].append(os.urandom(256))  # S-box state

        for _ in range(self.sbox_shuffle_rounds):
            seed = secrets.token_bytes(64)
            random_bytes = [os.urandom(256) for _ in range(2)]
            self.states['sbox_shuffle_rounds_states'].append({'seed': seed, 'sbox_left': random_bytes[0], 'sbox_right': random_bytes[1]})
        return self.states

    def pkcs7_pad(self, data):
        """Add PKCS type padding."""
        padding_length = self.block_size - (len(data) % self.block_size)
        if 0 < padding_length < 16:
            return data + bytes([padding_length]) * padding_length
        else:
            return data

    def pkcs7_unpad(self, data):
        """Remove PKCS type padding."""
        padding_length = data[-1]
        if 1 < padding_length < self.block_size:
            if all(byte == padding_length for byte in data[-padding_length:]):
                return data[:-padding_length]
        else:
            return data

    def encrypt_block(self, data):
        """Encrypt a block of data."""
        current_data = bytearray()
        chunks = list(self.read_in_chunks(bytearray(data)))

        for chunk in chunks:
            encrypted_chunk = self.pkcs7_pad(chunk)

            # S-box encryption rounds
            for state in self.states['sbox_rounds_states']:
                sbox = self.create(state)
                for index, byte in enumerate(encrypted_chunk):
                    encrypted_chunk[index] = sbox[byte]

            # Shuffle rounds
            for state in self.states['sbox_shuffle_rounds_states']:
                random.seed(state['seed'])
                sbox_left = self.create(state['sbox_left'])
                sbox_right = self.create(state['sbox_right'])
                for index, byte in enumerate(encrypted_chunk):
                    if random.randint(0, 999999) % 2 == 0:
                        encrypted_chunk[index] = sbox_left[byte]
                    else:
                        encrypted_chunk[index] = sbox_right[byte]

            current_data.extend(encrypted_chunk)
        return current_data

    def decrypt_block(self, encrypted_data, key=None):
        """Decrypt a block of data."""
        current_data = bytearray()
        chunks = self.read_in_chunks(bytearray(encrypted_data))

        if key is not None:
            self.states = key

        for chunk in chunks:
            # Reverse shuffle rounds
            for state in reversed(self.states['sbox_shuffle_rounds_states']):
                random.seed(state['seed'])
                sbox_left = self.create(state['sbox_left'])
                sbox_right = self.create(state['sbox_right'])
                sboxinv_left = self.invert(sbox_left)
                sboxinv_right = self.invert(sbox_right)
                for index, byte in enumerate(chunk):
                    if random.randint(0, 999999) % 2 == 0:
                        chunk[index] = sboxinv_left[byte]
                    else:
                        chunk[index] = sboxinv_right[byte]

            # Reverse S-box encryption rounds
            for state in reversed(self.states['sbox_rounds_states']):
                sbox = self.create(state)
                sboxinv = self.invert(sbox)
                for index, byte in enumerate(chunk):
                    chunk[index] = sboxinv[byte]

            current_data.extend(chunk)

        return self.pkcs7_unpad(current_data)
