import hashlib
from os import urandom
from secrets import randbelow

from tinyec import registry
from Crypto.Cipher import AES

# Getting a curve (a, b, p, G, n)
curve = registry.get_curve("secp256r1")


class ProtocolUser:
    def __init__(self, name: str):
        self.name = name
        # private key: [1, n-1]
        self.private_key = randbelow(curve.field.n - 1) + 1
        # Public key: Q = d × G (скалярне множення спільної точки)
        self.public_key = self.private_key * curve.g
        self.shared_secret = None

    def compute_shared_secret(self, other_public_key):
        self.shared_secret = self.private_key * other_public_key
        return self.shared_secret

    def derive_key(self, salt=None, info=b"ecdh-key", length=32):
        if self.shared_secret is None:
            raise ValueError("shared_secret не обчислено — спочатку викличте compute_shared_secret()")
        return self.hkdf_derive_key(self.shared_secret, salt=salt, info=info, length=length)

    def print_keys(self):
        """Вивести ключі учасника."""
        print(f"\n{'='*60}")
        print(f"  {self.name}")
        print(f"{'='*60}")
        print(f"  Приватний ключ (d):")
        print(f"    {hex(self.private_key)}")
        print(f"  Публічний ключ (Q = d × G):")
        print(f"    x = {hex(self.public_key.x)}")
        print(f"    y = {hex(self.public_key.y)}")

    @staticmethod
    def hkdf_derive_key(shared_point, salt=None, info=b"ecdh-key", length=32):
        if salt is None:
            salt = b'\x00' * 32
        prk = hashlib.sha256(salt + shared_point.x.to_bytes(32, 'big')).digest()
        key = hashlib.sha256(prk + info + b'\x01').digest()[:length]
        return key

    @staticmethod
    def encrypt(key: bytes, plaintext: str, nonce: bytes = None):
        if nonce is None:
            nonce = urandom(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        return nonce, ciphertext, tag

    @staticmethod
    def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> str:
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')


if __name__ == "__main__":
    # === ПРОТОКОЛ ECDH ===

    print("ПАРАМЕТРИ КРИВОЇ secp256r1:")
    print(f"  p = {hex(curve.field.p)}")
    print(f"  a = {curve.a}")
    print(f"  b = {hex(curve.b)}")
    print(f"  G.x = {hex(curve.g.x)}")
    print(f"  G.y = {hex(curve.g.y)}")
    print(f"  n = {hex(curve.field.n)}")

    # Крок 1: Генерація ключових пар
    alice = ProtocolUser("Аліса")
    bob = ProtocolUser("Боб")

    alice.print_keys()
    bob.print_keys()

    # Крок 2: Обмін публічними ключами та обчислення спільного секрету
    alice_secret = alice.compute_shared_secret(bob.public_key)
    bob_secret = bob.compute_shared_secret(alice.public_key)

    # Крок 3: Перевірка
    print(f"\n{'='*60}")
    print(f"  СПІЛЬНИЙ СЕКРЕТ")
    print(f"{'='*60}")
    print(f"  Аліса обчислила S = dₐ × Q_b:")
    print(f"    x = {hex(alice_secret.x)}")
    print(f"    y = {hex(alice_secret.y)}")
    print(f"\n  Боб обчислив S = d_b × Qₐ:")
    print(f"    x = {hex(bob_secret.x)}")
    print(f"    y = {hex(bob_secret.y)}")
    print(f"\n  Секрети збігаються: {alice_secret == bob_secret}")

    # === ДЕРИВАЦІЯ КЛЮЧА ===
    alice_key = alice.derive_key()
    bob_key = bob.derive_key()

    print(f"\n{'='*60}")
    print(f"  ДЕРИВАЦІЯ КЛЮЧА (HKDF)")
    print(f"{'='*60}")
    print(f"  Ключ Аліси:  {alice_key.hex()}")
    print(f"  Ключ Боба:   {bob_key.hex()}")
    print(f"  Ключі збігаються: {alice_key == bob_key}")

    # === ШИФРУВАННЯ AES-256-GCM ===
    message = "Привіт, Бобе! Це секретне повідомлення."
    nonce, ciphertext, tag = ProtocolUser.encrypt(alice_key, message)

    print(f"\n{'='*60}")
    print(f"  ШИФРУВАННЯ (AES-256-GCM)")
    print(f"{'='*60}")
    print(f"  Оригінал:    {message}")
    print(f"  Nonce:       {nonce.hex()}")
    print(f"  Шифротекст:  {ciphertext.hex()}")
    print(f"  Tag:         {tag.hex()}")

    # === ДЕШИФРУВАННЯ ===
    decrypted = ProtocolUser.decrypt(bob_key, nonce, ciphertext, tag)

    print(f"\n{'='*60}")
    print(f"  ДЕШИФРУВАННЯ")
    print(f"{'='*60}")
    print(f"  Боб отримав: {decrypted}")
    print(f"\n  Повідомлення збігається: {message == decrypted}")
