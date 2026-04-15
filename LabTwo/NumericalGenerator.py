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
        n = p*q
        
        if math.gcd(seed, n) != 1:
            print("Числа повинні бути взаємно простими (не мати спільних дільників окрім 1) ...")
            return
        x = pow(seed, 2, n)
        bits = []
        for _ in range(number_of_bits):
            x = pow(x, 2, n)
            bits.append(str(x & 1))
        return "".join(bits) 
    
    @staticmethod
    def get_entropy_from_binance(lemer_value):
        url = "https://api.binance.com/api/v3/ticker/price?symbol=XMRUSDT"
        response = requests.get(url)
        price = response.json()['price']

        price_int = int(price.replace('.', ''))
        timestamp = time.time_ns()
        entropy = price_int ^ timestamp ^ lemer_value
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
            binary_string = bitstream[_:_+chunk_size]
            number = int(binary_string, 2)
            numbers.append(number)
        return numbers


if __name__ == "__main__":
    num_gen = NumericalGenerator()
    
    # ── Lemer ──
    modulus = 2147483647
    multi = 16807
    n = 33000  
    num_streams_lemer = 1

    seeds_lemer = [i * 1000 + 7 for i in range(1, num_streams_lemer + 1)]

    with open("/home/siercig/University/Cryptography/LabTwo/lemer_bits3.txt", 'w') as file:
        for seed in seeds_lemer:
            generated = num_gen.LemerGenerator(n=n, multi=multi, modulus=modulus, seed=seed)
            bits = num_gen.numbers_to_bitsream(generated)
            file.write(bits + '\n')
    
    # ── BBS ──
    p = 2147483659   
    q = 2147483743   
    
    num_streams_bbs = 55
    bits_per_stream = 1_000_000

    random.seed(42)
    seeds_bbs = random.sample(range(2, p * q), num_streams_bbs)

    with open("/home/siercig/University/Cryptography/LabTwo/bbs_bits3.txt", 'w') as file:
        for s in seeds_bbs:
            if math.gcd(s, p * q) == 1:
                bits = num_gen.BBS(p=p, q=q, seed=s, number_of_bits=bits_per_stream)
                if bits:
                    file.write(bits + '\n')

    print("Обычный BBS готово")

    # ── BBS с энтропией Binance + Lemer ──
    lemer_entropy_sequence = num_gen.LemerGenerator(n=num_streams_bbs, multi=16807, modulus=2147483647, seed=99991)

    with open("/home/siercig/University/Cryptography/LabTwo/bbs_binance_bits3.txt", 'w') as file:
        for i in range(num_streams_bbs):
            raw_entropy = num_gen.get_entropy_from_binance(lemer_entropy_sequence[i])
            
            s = (raw_entropy % (p * q - 2)) + 2

            while math.gcd(s, p * q) != 1:
                s = (s + 1) % (p * q)

            bits = num_gen.BBS(p=p, q=q, seed=s, number_of_bits=bits_per_stream)
            if bits:
                file.write(bits + '\n')

            print(f"BBS Binance Stream {i + 1}/{num_streams_bbs} | seed={s}")
            time.sleep(0.1)

    print("BBS Binance готово")