import os
import random


class ShadowSystem:
    def __init__(self, sbox_rounds=50, sbox_shuffle_rounds=25, block_size=2048):
        self.sbox_rounds = sbox_rounds
        self.sbox_shuffle_rounds = sbox_shuffle_rounds
        self.random_bytes = os.urandom(256)
        self.block_size = block_size
        self.states = []

    def invert(self, sbox):
        sboxinv = [i for i in range(0, 256)]
        for index, value in enumerate(sbox):
            sboxinv[value] = index
        return sboxinv

    def create(self, state):
        sbox = [i for i in range(0, 256)]
        for index, number in enumerate(sbox):
            for random_byte in state:
                # Swap
                sbox[random_byte], sbox[index] = sbox[index], sbox[random_byte]
        return sbox

    def set_cipher_states(self):
        for i in range(0, self.sbox_rounds):
            self.states.append(self.random_bytes)
            self.random_bytes = os.urandom(256)

        for i in range(0, self.sbox_shuffle_rounds):
            seed = os.urandom(64)
            self.random_bytes = [[i for i in os.urandom(256)] for i in range(2)]
            self.states.append(seed)
            self.states.append(self.random_bytes)

        return self.states

    def encrypt_block(self, data):
        current_data = bytearray(data)
        current_data_remainder = len(current_data) % self.block_size

        if current_data_remainder != 0:
            current_data_remainder = self.block_size - current_data_remainder - 2
            current_data.append(0x95)
            current_data.append(0xAF)
            for i in range(0, current_data_remainder):
                current_data.append(0XFF)

        for state in self.states[:self.sbox_rounds]:
            sbox = self.create(state)
            for index, byte in enumerate(current_data):
                current_data[index] = sbox[byte]

        seed = bytes()
        for state in self.states[self.sbox_shuffle_rounds * 2:]:
            if isinstance(state, list):
                random.seed(seed)
                sbox_left = self.create(state[0])
                sbox_right = self.create(state[1])
                for index, byte in enumerate(current_data):
                    magic_number = random.randint(0, 100)
                    if magic_number % 2 == 0:
                        current_data[index] = sbox_left[byte]
                    else:
                        current_data[index] = sbox_right[byte]
            else:
                seed = state

        return current_data

    def decrypt_block(self, key, encrypted_data):
        current_data = bytearray(encrypted_data)

        states = key.copy()
        for i in range(self.sbox_rounds + (self.sbox_shuffle_rounds * 2)-1, (self.sbox_shuffle_rounds * 2), -2):
            states[i], states[i-1] = states[i-1], states[i]

        seed = bytes()
        for state in reversed(states[self.sbox_shuffle_rounds * 2:]):
            if isinstance(state, list):
                random.seed(seed)
                sbox_left = self.create(state[0])
                sbox_right = self.create(state[1])
                sboxinv_left = self.invert(sbox_left)
                sboxinv_right = self.invert(sbox_right)
                for index, byte in enumerate(current_data):
                    magic_number = random.randint(0, 100)
                    if magic_number % 2 == 0:
                        current_data[index] = sboxinv_left[byte]
                    else:
                        current_data[index] = sboxinv_right[byte]
            else:
                seed = state

        for state in reversed(states[:self.sbox_rounds]):
            sbox = self.create(state)
            sboxinv = self.invert(sbox)
            for index, byte in enumerate(current_data):
                current_data[index] = sboxinv[byte]

        #strip padding
        for index, byte in enumerate(current_data):
            if current_data[index] == 0x95 and current_data[index + 1] == 0xAF and current_data[index + 2] == 0xFF:
                current_data = current_data[:index]
                break

        return current_data
