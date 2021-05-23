import os


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
        for i in range(0, 100):
            current_state = [i for i in self.random_bytes]
            sbox = self.create(current_state)
            for index, byte in enumerate(current_data):
                current_data[index] = sbox[byte]
            self.states.append(self.random_bytes)
            self.random_bytes = os.urandom(256)

        return self.states, current_data

    def decrypt(self, states, encrypted_data):
        current_data = bytearray(encrypted_data)
        for state in reversed(states):
            sbox = self.create(state)
            sboxinv = self.invert(sbox)
            for index, byte in enumerate(current_data):
                current_data[index] = sboxinv[byte]
        return current_data
