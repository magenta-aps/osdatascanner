import pytest

from os2datascanner.projects.admin.adminapp.aescipher import encrypt, decrypt
from os2datascanner.projects.admin.adminapp.models.authentication import Authentication


@pytest.mark.django_db
class TestAESCipher:

    def test_encrypt_decrypt(self):
        password_to_encrypt = 'hemmeligtpassword'
        iv, ciphertext = encrypt(password_to_encrypt)
        password_after_decrypt = decrypt(iv, ciphertext)
        assert password_to_encrypt == password_after_decrypt

    def test_storing_and_retrieving_authentication_data(self):
        password_to_encrypt = 'top_secret'
        iv, ciphertext = encrypt(password_to_encrypt)
        Authentication.objects.create(
            username='jasper',
            iv=iv,
            ciphertext=ciphertext
        )
        stored_auth = Authentication.objects.get(username='jasper')
        password_after_decrypt = decrypt(bytes(stored_auth.iv), bytes(stored_auth.ciphertext))
        assert password_to_encrypt == password_after_decrypt
