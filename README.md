# shadowsystem
ShadowSystem - an ephemeral symmetric cipher

ShadowSystem is an ephemeral symmetric cipher that encrypts data by passing it through 100 rounds of randomized(os.urandom) s-box and
then returns the ciphertext and random byte states used for the encryption which are then used as key for the decryption process. This cipher
is currently entirely experimental and in it's current state is **NOT RECOMMENDED** to be used in a production environment.
