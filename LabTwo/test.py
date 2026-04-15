import math
import random
import requests
import time
import os


class NumericalGenerator:
    def __init__(self):
        pass

    def LemerGenerator(self, n, multi, modulus, seed):
        assert 0 < seed < modulus, "seed must be in range (0, modulus)"
        prev = seed
        generated_sequence = []
        for i in range(n):
            value = (multi * prev) % modulus
            generated_sequence.append(value)
            prev = value
        return generated_sequence

    def BBS(self, p, q, seed, number_of_bits):
        if p % 4 != 3 or q % 4 != 3 or p == q:
            print("Повинні виконуватись умови ...")
            return
        n = p * q
        if math.gcd(seed, n) != 1:
            print("Числа повинні бути взаємно простими ...")
            return
        x = pow(seed, 2, n)
        bits = []
        for _ in range(number_of_bits):
            x = pow(x, 2, n)
            bits.append(str(x & 1))
        return "".join(bits)

    @staticmethod
    def get_entropy_from_binance():
        url = "https://api.binance.com/api/v3/ticker/price?symbol=XMRUSDT"
        response = requests.get(url)
        price = response.json()['price']

        price_int = int(price.replace('.', ''))
        timestamp = time.time_ns()
        entropy = price_int ^ timestamp ^ int.from_bytes(os.urandom(8), 'big')
        return entropy

    @staticmethod
    def numbers_to_bitsream(numbers, bit_width=31):
        bits = []
        for number in numbers:
            bits.append(format(number, f'0{bit_width}b'))
        return ''.join(bits)

    @staticmethod
    def bitsream_to_numbers(bitstream, chunk_size):
        numbers = []
        for _ in range(0, len(bitstream), chunk_size):
            binary_string = bitstream[_:_ + chunk_size]
            number = int(binary_string, 2)
            numbers.append(number)
        return numbers


if __name__ == "__main__":
    num_gen = NumericalGenerator()

    # ── Lemer ──
    # modulus = 2147483647
    # multi = 16807
    # n = 33000
    # num_streams = 55
    # seeds = [i * 1000 + 7 for i in range(1, num_streams + 1)]
    # with open("/home/siercig/University/Cryptography/LabTwo/lemer_bits.txt", 'w') as file:
    #     for seed in seeds:
    #         generated = num_gen.LemerGenerator(n=n, multi=multi, modulus=modulus, seed=seed)
    #         bits = num_gen.numbers_to_bitsream(generated)
    #         file.write(bits + '\n')

    # ── BBS з ентропією Binance ──
    p = 2147483659    # 1000000007 % 4 = 3 ✓
    q = 2147483743    # 1000000403 % 4 = 3 ✓

    bits_per_stream = 1_000_000
    num_streams = 55

    with open("/home/siercig/University/Cryptography/LabTwo/bbs_own_enthropy.txt", 'w') as file:
        for i in range(num_streams):
            raw_entropy = num_gen.get_entropy_from_binance()
            seed = raw_entropy % (p * q)

            while math.gcd(seed, p * q) != 1:
                seed = (seed + 1) % (p * q)

            bits = num_gen.BBS(p=p, q=q, seed=seed, number_of_bits=bits_per_stream)
            if bits:
                file.write(bits + '\n')

            print(f"Stream {i + 1}/{num_streams} | seed={seed}")
            time.sleep(0.1)

    print("BBS готово")