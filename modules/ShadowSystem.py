import os
import random


class ShadowSystem:
    def __init__(self):
        self.random_bytes = os.urandom(256)
        self.states = []

    def invert(self, sbox):
        sboxinv = [i for i in range(0,256)]
        for index, value in enumerate(sbox):
            sboxinv[value] = index
        return sboxinv

    def create(self, state):
        sbox = [i for i in range(0,256)]
        for index, number in enumerate(sbox):
            for random_byte in state:
                # Swap
                sbox[random_byte], sbox[index] = sbox[index], sbox[random_byte]
        return sbox

    def encrypt(self, data):
        current_data = bytearray(data)
        seed = os.urandom(64)
        random.seed(seed)
        magic_numbers = []
        for i in range(0, 50):
            current_state = [i for i in self.random_bytes]
            sbox = self.create(current_state)
            for index, byte in enumerate(current_data):
                current_data[index] = sbox[byte]
            self.states.append(self.random_bytes)
            self.random_bytes = os.urandom(256)

        for i in range(0, 25):
            self.random_bytes = [[i for i in os.urandom(256)] for i in range(2)]
            self.states.append(self.random_bytes)
            sbox_left = self.create(self.random_bytes[0])
            sbox_right = self.create(self.random_bytes[1])
            for index, byte in enumerate(current_data):
                magic_number = random.randint(0, 100)
                magic_numbers.append(magic_number)
                if magic_number % 2 == 0:
                    current_data[index] = sbox_left[byte]
                else:
                    current_data[index] = sbox_right[byte]
            self.states.append(magic_numbers)
            magic_numbers = []

        return self.states, current_data

    def decrypt(self, states, encrypted_data):
        current_data = bytearray(encrypted_data)
        current_magic_numbers = []
        for state in reversed(states[-50:]):
            if any(isinstance(i, list) for i in state):
                sbox_left = self.create(state[0])
                sbox_right = self.create(state[1])
                sboxinv_left = self.invert(sbox_left)
                sboxinv_right = self.invert(sbox_right)
                for index, byte in enumerate(current_data):
                    if current_magic_numbers[index] % 2 == 0:
                        current_data[index] = sboxinv_left[byte]
                    else:
                        current_data[index] = sboxinv_right[byte]
            else:
                current_magic_numbers = state

        for state in reversed(states[:-50]):
            sbox = self.create(state)
            sboxinv = self.invert(sbox)
            for index, byte in enumerate(current_data):
                current_data[index] = sboxinv[byte]

        return current_data
