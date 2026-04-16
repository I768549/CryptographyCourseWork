import hashlib
import random
from math import gcd

from Crypto.Util.number import getPrime


class RSA:
    @staticmethod
    def generate_primes(bits: int = 256) -> tuple[int, int]:
        """Генерує пару простих чисел заданої розрядності (Miller-Rabin)."""
        return getPrime(bits), getPrime(bits)

    def __init__(self, p: int, q: int, e: int = 65537):
        self.p = p
        self.q = q
        self.e = e
        # розраховуємо значення функції Ейлера
        phi = (p-1)*(q-1)
        #d = e⁻¹ mod φ(n) — обернений елемент існує тільки коли gcd(e, φ(n)) = 1.
        if gcd(self.e, phi) !=1:
            raise ValueError(f"e={self.e} не є взаємно простим з φ(n)={phi}")
        self.d = pow(self.e, -1, phi)
        self.n = p * q
        
    def sign(self, message: str):
        """Створення підпису: s = SHA-256(m)^d mod n."""
        #Переводимо строку в байти, розраховуємо 256 хеш, переводимо в hex строку, переводимо в число
        h = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
        # d = e⁻¹ mod φ(n) — обернений елемент
        return pow(h, self.d, self.n)
    
    def verify_signature(self, message: str, signature: int) -> bool:
        """Перевірка підпису: SHA-256(m) == s^e mod n."""
        h = int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)
        return h == pow(signature, self.e, self.n)