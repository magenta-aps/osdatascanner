import secrets
from Crypto.Util import Counter
from Crypto.Cipher import AES


def encrypt(plaintext: str, key: str | bytes) -> (bytes, bytes):
    """Encrypts the given plaintext using the given 32-byte key. (The
    underlying cipher is AES in counter mode.)

    Returns a randomly-generated initialisation vector along with the
    resulting ciphertext; 6decryption will require both of these values."""

    if isinstance(key, str):
        key = bytes.fromhex(key)

    # Choose a random, 16-byte IV.
    iv_int: int = secrets.randbits(8 * AES.block_size)
    iv: bytes = iv_int.to_bytes(AES.block_size, 'big')

    # Create a new Counter object with IV = iv_int.
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Encrypt and return IV and ciphertext.
    ciphertext = aes.encrypt(plaintext.encode())
    return (iv, ciphertext)


def decrypt(iv: bytes, ciphertext: bytes, key: str | bytes) -> str:
    """Decrypts the result of a previous call to the encrypt() function."""

    if isinstance(key, str):
        key = bytes.fromhex(key)

    # Initialize counter for decryption. iv should be the same as the output of
    # encrypt().
    iv_int: int = int.from_bytes(iv, 'big')
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Decrypt and return the plaintext.
    plaintext = aes.decrypt(ciphertext)
    return plaintext.decode('utf-8')
