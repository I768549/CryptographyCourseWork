from LabTwo.NumericalGenerator import NumericalGenerator


def generate_key_stream(seed, length):
    """Генерація ключового потоку за допомогою генератора Лемера."""
    gen = NumericalGenerator()
    modulus = 2147483647
    multi = 16807
    raw = gen.LemerGenerator(n=length, multi=multi, modulus=modulus, seed=seed)
    # Обрізаємо кожне число до 8 біт (0-255) для XOR з байтами
    return [val % 256 for val in raw]


def encrypt(plaintext: str, initial_seed: int, key_change_interval: int = 5) -> bytes:
    """
    Шифрування тексту побітовим XOR з ключовим потоком.
    Ключ змінюється кожні key_change_interval символів.
    """
    data = plaintext.encode("utf-8")
    ciphertext = bytearray()

    current_seed = initial_seed
    pos = 0

    while pos < len(data):
        # Визначаємо розмір поточного блоку
        block_size = min(key_change_interval, len(data) - pos)

        # Генеруємо ключовий потік для блоку
        key_stream = generate_key_stream(current_seed, block_size)

        # XOR кожного байту блоку з ключовим потоком
        for i in range(block_size):
            ciphertext.append(data[pos + i] ^ key_stream[i])

        # Змінюємо seed для наступного блоку
        # Новий seed = останнє значення генератора + номер блоку
        current_seed = (current_seed * 31 + pos + 1) % 2147483646 + 1

        pos += block_size

    return bytes(ciphertext)


def decrypt(ciphertext: bytes, initial_seed: int, key_change_interval: int = 5) -> str:
    """
    Дешифрування — симетрична операція (XOR з тим самим ключовим потоком).
    """
    plaintext = bytearray()

    current_seed = initial_seed
    pos = 0

    while pos < len(ciphertext):
        block_size = min(key_change_interval, len(ciphertext) - pos)

        key_stream = generate_key_stream(current_seed, block_size)

        for i in range(block_size):
            plaintext.append(ciphertext[pos + i] ^ key_stream[i])

        current_seed = (current_seed * 31 + pos + 1) % 2147483646 + 1

        pos += block_size

    return plaintext.decode("utf-8")


def main():
    print("=" * 60)
    print("  Варіант 1. Базовий потоковий шифр на основі XOR")
    print("  ГПВЧ: генератор Лемера (з лабораторної роботи №2)")
    print("=" * 60)

    initial_seed = 12345
    key_change_interval = 5

    # --- Тест 1: Латиниця ---
    text1 = "Hello, World! This is a XOR stream cipher test."
    print(f"\n[Тест 1] Оригінальний текст: {text1}")

    enc1 = encrypt(text1, initial_seed, key_change_interval)
    print(f"Зашифрований (hex):          {enc1.hex()}")

    dec1 = decrypt(enc1, initial_seed, key_change_interval)
    print(f"Розшифрований текст:          {dec1}")
    print(f"Збігається з оригіналом:      {dec1 == text1}")

    # --- Тест 2: Кирилиця ---
    text2 = " ест шифрування кирилицею"
    print(f"\n[Тест 2] Оригінальний текст: {text2}")

    enc2 = encrypt(text2, initial_seed, key_change_interval)
    print(f"Зашифрований (hex):          {enc2.hex()}")

    dec2 = decrypt(enc2, initial_seed, key_change_interval)
    print(f"Розшифрований текст:          {dec2}")
    print(f"Збігається з оригіналом:      {dec2 == text2}")

    # --- Тест 3: Порожній рядок ---
    text3 = ""
    print(f"\n[Тест 3] Порожній рядок")
    enc3 = encrypt(text3, initial_seed, key_change_interval)
    dec3 = decrypt(enc3, initial_seed, key_change_interval)
    print(f"Збігається з оригіналом:      {dec3 == text3}")

    # --- Тест 4: Демонстрація зміни ключа ---
    print(f"\n[Тест 4] Демонстрація зміни ключа кожні {key_change_interval} символів")
    text4 = "ABCDEFGHIJKLMNO"  # 15 символів = 3 блоки по 5
    print(f"Текст: {text4} ({len(text4)} символів, {len(text4) // key_change_interval} блоки)")

    seed = initial_seed
    data = text4.encode("utf-8")
    for block_num in range(0, len(data), key_change_interval):
        block = data[block_num : block_num + key_change_interval]
        ks = generate_key_stream(seed, len(block))
        encrypted_block = bytes([b ^ k for b, k in zip(block, ks)])
        print(
            f"  Блок {block_num // key_change_interval + 1}: "
            f"seed={seed:>10}, "
            f"текст={block.decode()!r:>7}, "
            f"ключовий потік={ks}, "
            f"шифротекст={encrypted_block.hex()}"
        )
        seed = (seed * 31 + block_num + 1) % 2147483646 + 1

    enc4 = encrypt(text4, initial_seed, key_change_interval)
    dec4 = decrypt(enc4, initial_seed, key_change_interval)
    print(f"Розшифрований текст: {dec4}")
    print(f"Збігається з оригіналом: {dec4 == text4}")

    # --- Підсумок ---
    all_passed = (dec1 == text1) and (dec2 == text2) and (dec3 == text3) and (dec4 == text4)
    print("\n" + "=" * 60)
    if all_passed:
        print("  Усі тести пройдено успішно")
    else:
        print("  Не всі тести не пройдено")
    print("=" * 60)


if __name__ == "__main__":
    main()
