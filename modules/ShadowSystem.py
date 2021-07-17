import os
import random


class ShadowSystem:
    def __init__(self, sbox_rounds=16, sbox_shuffle_rounds=8, block_size=1024):
        self.PAD_BYTE = 0x00
        self.MAGIC_BYTE = 0xB2
        self.sbox_rounds = sbox_rounds
        self.sbox_shuffle_rounds = sbox_shuffle_rounds
        self.block_size = block_size
        self.random_bytes = os.urandom(256)
        self.states = []

    @staticmethod
    def invert(sbox):
        sboxinv = [i for i in range(0,256)]
        for index, value in enumerate(sbox):
            sboxinv[value] = index
        return sboxinv

    @staticmethod
    def create(state):
        sbox = [i for i in range(0,256)]
        for index, number in enumerate(sbox):
            for random_byte in state:
                # Swap
                sbox[random_byte], sbox[index] = sbox[index], sbox[random_byte]
        return sbox

    def encrypt(self, data):
        current_data = bytearray(data)
        if len(current_data) < self.block_size:
            pad_length = self.block_size - len(current_data)
            pad_length_byte = int(pad_length / 255)
            pad_remainder_byte = pad_length % 255
            if pad_length > 4:
                for i in range(0, pad_length - pad_length_byte - 3):
                    current_data.append(self.PAD_BYTE)
                for i in range(0, pad_length_byte):
                    current_data.append(0xFF)
                current_data.append(pad_remainder_byte)
                current_data.append(pad_length_byte + 1)
                current_data.append(self.MAGIC_BYTE)
            elif pad_length <= 4:
                for i in range(0, pad_length):
                    current_data.append(self.MAGIC_BYTE)
        elif len(current_data) > self.block_size:
            raise Exception("Invalid block size for encrypt method, should be %d bytes or less, got %d bytes." % (self.block_size, len(current_data)))
        for i in range(0, self.sbox_rounds):
            current_state = [i for i in self.random_bytes]
            sbox = self.create(current_state)
            for index, byte in enumerate(current_data):
                current_data[index] = sbox[byte]
            self.states.append(self.random_bytes)
            self.random_bytes = os.urandom(256)

        for i in range(0, self.sbox_shuffle_rounds):
            seed = os.urandom(64)
            random.seed(seed)
            self.random_bytes = [[i for i in os.urandom(256)] for i in range(2)]
            self.states.append(self.random_bytes)
            sbox_left = self.create(self.random_bytes[0])
            sbox_right = self.create(self.random_bytes[1])
            for index, byte in enumerate(current_data):
                magic_number = random.randint(0, 100)
                if magic_number % 2 == 0:
                    current_data[index] = sbox_left[byte]
                else:
                    current_data[index] = sbox_right[byte]
            self.states.append(seed)

        return self.states, current_data

    def decrypt(self, states, encrypted_data):
        current_data = bytearray(encrypted_data)
        if len(current_data) < self.block_size:
            raise Exception("Invalid block size for decrypt method, should be %d bytes, got %d bytes." % (self.block_size, len(current_data)))
        elif len(current_data) > self.block_size:
            raise Exception("Invalid block size for decrypt method, should be %d bytes, got %d bytes." % (self.block_size, len(current_data)))
        else:
            if current_data[-1] == self.MAGIC_BYTE:
                pad_length = 0
                current_data.pop()
                data_iter = iter(reversed(current_data))
                while data_iter:
                    current_data_byte = next(data_iter)
                    if current_data_byte == self.MAGIC_BYTE:
                        pad_length += 1
                    else:
                        for i in range(0, current_data_byte):
                            pad_length += current_data_byte
                current_data = current_data[len(current_data) - pad_length:]
        seed = bytes()
        for state in reversed(states[-(self.sbox_shuffle_rounds * 2):]):
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

        for state in reversed(states[:-self.sbox_rounds]):
            sbox = self.create(state)
            sboxinv = self.invert(sbox)
            for index, byte in enumerate(current_data):
                current_data[index] = sboxinv[byte]

        return current_data
