# shadowsystem
ShadowSystem - an ephemeral symmetric block cipher

ShadowSystem is an ephemeral symmetric block cipher that encrypts data by passing it through 50 rounds of randomized(os.urandom) s-box, 25 rounds of randomized s-box shuffle and then returns the ciphertext and random byte states used for the encryption which are then used as key for the decryption process. This cipher
is currently entirely experimental and in it's current state is **NOT RECOMMENDED** to be used in a production environment.
