#!/usr/bin/env python3
"""
Скрипт для завантаження правильних S-box'ів Калини з GitHub
та їх вставки в kalyna.py

Запуск:
    python3 fetch_and_fix.py

Потрібен доступ до інтернету.
"""
import urllib.request
import re
import sys

URL = "https://raw.githubusercontent.com/Roman-Oliynykov/Kalyna-reference/master/tables.c"

print("Завантаження tables.c з GitHub...")
try:
    resp = urllib.request.urlopen(URL)
    data = resp.read().decode('utf-8')
except Exception as e:
    print(f"Помилка завантаження: {e}")
    print("Спробуйте завантажити вручну:")
    print(f"  wget {URL}")
    sys.exit(1)

# Парсинг S-box'ів
# Шукаємо sboxes_enc[4][256]
sbox_pattern = r'sboxes_enc\[4\]\[256\]\s*=\s*\{(.*?)\};'
match = re.search(sbox_pattern, data, re.DOTALL)
if not match:
    print("Не знайдено sboxes_enc в tables.c")
    sys.exit(1)

sbox_data = match.group(1)
# Extract individual hex values
hex_values = re.findall(r'0x[0-9a-fA-F]+', sbox_data)

if len(hex_values) != 1024:  # 4 * 256
    print(f"Очікувалось 1024 значень, знайдено {len(hex_values)}")
    sys.exit(1)

# Split into 4 S-boxes
sboxes = []
for i in range(4):
    sbox = [int(v, 16) for v in hex_values[i*256:(i+1)*256]]
    sboxes.append(sbox)

# Verify bijectivity
for i, sbox in enumerate(sboxes):
    if len(set(sbox)) != 256:
        print(f"ПОМИЛКА: S-box {i} не бієктивний!")
        sys.exit(1)
    print(f"S-box {i}: OK (бієктивний)")

# Parse inverse S-boxes
inv_pattern = r'sboxes_dec\[4\]\[256\]\s*=\s*\{(.*?)\};'
inv_match = re.search(inv_pattern, data, re.DOTALL)

# Parse MDS matrix
mds_pattern = r'mds_matrix\[8\]\[8\]\s*=\s*\{(.*?)\};'
mds_match = re.search(mds_pattern, data, re.DOTALL)

mds_inv_pattern = r'mds_inv_matrix\[8\]\[8\]\s*=\s*\{(.*?)\};'
mds_inv_match = re.search(mds_inv_pattern, data, re.DOTALL)

# Generate Python code
print("\nГенерація Python-коду...")

def format_sbox(sbox, name):
    lines = [f"    # {name}"]
    lines.append("    [")
    for row in range(16):
        vals = sbox[row*16:(row+1)*16]
        line = "        " + ", ".join(f"0x{v:02x}" for v in vals) + ","
        lines.append(line)
    lines.append("    ],")
    return "\n".join(lines)

output = "S_BOX_ENC = [\n"
for i in range(4):
    output += format_sbox(sboxes[i], f"S{i}") + "\n"
output += "]\n"

with open('kalyna_sboxes.py', 'w') as f:
    f.write(output)

print(f"Збережено в kalyna_sboxes.py")

if mds_match:
    mds_vals = re.findall(r'0x[0-9a-fA-F]+', mds_match.group(1))
    mds = [[int(v, 16) for v in mds_vals[i*8:(i+1)*8]] for i in range(8)]
    with open('kalyna_sboxes.py', 'a') as f:
        f.write("\nMDS_MATRIX = [\n")
        for row in mds:
            f.write("    [" + ", ".join(f"0x{v:02X}" for v in row) + "],\n")
        f.write("]\n")
    print("MDS матриця збережена")

if mds_inv_match:
    inv_vals = re.findall(r'0x[0-9a-fA-F]+', mds_inv_match.group(1))
    inv_mds = [[int(v, 16) for v in inv_vals[i*8:(i+1)*8]] for i in range(8)]
    with open('kalyna_sboxes.py', 'a') as f:
        f.write("\nMDS_INV_MATRIX = [\n")
        for row in inv_mds:
            f.write("    [" + ", ".join(f"0x{v:02X}" for v in row) + "],\n")
        f.write("]\n")
    print("Обернена MDS матриця збережена")

print("\nГотово! Тепер скопіюйте вміст kalyna_sboxes.py в kalyna.py")
print("замінивши відповідні масиви S_BOX_ENC, MDS_MATRIX, MDS_INV_MATRIX")