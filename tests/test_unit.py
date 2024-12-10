import unittest
from modules.ShadowSystem import ShadowSystem


class TestShadowSystem(unittest.TestCase):
    def setUp(self):
        self.cipher = ShadowSystem()
        self.cipher.set_cipher_states()

    def test_encryption_decryption(self):

        plaintext = b"Test Data" * 100
        print(f"Plaintext: {plaintext}")
        encrypted = self.cipher.encrypt_block(plaintext)
        print(f"Encrypted: {encrypted}")
        decrypted = self.cipher.decrypt_block(encrypted, self.cipher.states)
        print(f"Decrypted: {decrypted}")

        self.assertEqual(decrypted, plaintext, "Decryption failed!")


if __name__ == '__main__':
    unittest.main()
