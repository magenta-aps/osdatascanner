import binascii, os, logging
from Crypto.Util import Counter
from Crypto.Cipher import AES
from Crypto import Random

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def encrypt(plaintext):
    """
    Takes as input a 32-byte key and an arbitrary-length plaintext and returns a
    pair (iv, ciphtertext). "iv" stands for initialization vector.
    """
    key = get_key()

    # Choose a random, 16-byte IV.
    iv = Random.new().read(AES.block_size)

    # Convert the IV to a Python integer.
    iv_int = int(binascii.hexlify(iv), 16)

    # Create a new Counter object with IV = iv_int.
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Encrypt and return IV and ciphertext.
    ciphertext = aes.encrypt(plaintext.encode())
    return (iv, ciphertext)


def decrypt(iv, ciphertext):
    """
    Takes as input a 32-byte key, a 16-byte IV, and a ciphertext, and outputs
    the corresponding plaintext.
    """
    key = get_key()

    # Initialize counter for decryption. iv should be the same as the output of
    # encrypt().
    iv_int = int(binascii.hexlify(iv), 16)
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Decrypt and return the plaintext.
    plaintext = aes.decrypt(ciphertext)
    return plaintext.decode('utf-8')


def get_key():
    key = None
    logger.info("Retrieving key via config")
    if settings.DECRYPTION_HEX:
        key = bytes.fromhex(settings.DECRYPTION_HEX)
    else:
        _email_admin(
            "CRITICAL!",
            "The configuration key DECRYPTION_HEX is not set!\n\n" +
            "If the system has previously used a file to store the key for " +
            "decryption, the hex value can be retrieved by calling:\n\n" +
            "\tos2datascanner.projects.admin.adminapp.aescipher." +
            "get_hex_from_key_file(<full key_file path>\n\n" +
            "If not, a new value can be generated by calling:\n\n"
            "\tos2datascanner.projects.admin.adminapp.aescipher." +
            "generate_new_hex()\n\n" +
            "The hex value should be stored in user-settings.toml:\n\n" +
            "DECRYPTION_HEX = \"<hex value>\""
        )
        raise ImproperlyConfigured("The setting DECRYPTION_HEX is empty")
    return key


def generate_new_hex():
    # AES supports multiple key sizes: 16 (AES128), 24 (AES192), or 32 (AES256).
    key_bytes = 32
    key = Random.new().read(key_bytes)
    return key.hex()


def _email_admin(subject, body):
    try:
        message = EmailMessage(subject, body, settings.ADMIN_EMAIL)
        message.send()
    except Exception as ex:
        logger.error(
            'Error occurred while sending email to administrator.'.format(ex)
        )


def get_hex_from_key_file(file_name):
    key = None
    if os.path.isfile(file_name):
        key = key_file_handling(None, 'rb', file_name, False)
    else:

        _email_admin('CRITICAL!', 'New master key has been generated.')

    return key


def key_file_handling(data, command, filename, create):
    file = None
    try:
        if create and not os.path.isfile(filename):
            os.mknod(filename)
        file = open(filename, command)
        if command == 'rb':
            data = file.read()
        elif command == 'ab':
            file.write(data)
    except (OSError, IOError) as ex:
        logger.error('An error occured while trying to {0} {1} file. {2}'.format(command, filename, ex))
    finally:
        if file is not None:
            file.close()
    return data
