import os

input_path = "/home/siercig/University/Cryptography/LabTwo/secrets_bits.bin"
output_path = "/home/siercig/University/Cryptography/LabTwo/secrets_bits_padded.bin"

target_bytes_per_stream = 131072          # 1,048,576 bits / 8
original_bytes_per_stream = 1_000_000 // 8  # 125,000
pad_bytes_per_stream = target_bytes_per_stream - original_bytes_per_stream  # = 6,072

total_original_bytes = os.path.getsize(input_path)
num_streams = total_original_bytes // original_bytes_per_stream  # should be 55

with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
    for i in range(num_streams):
        chunk = fin.read(original_bytes_per_stream)
        if len(chunk) < original_bytes_per_stream:
            print(f"Warning: incomplete chunk at stream {i+1}")
            break
        fout.write(chunk)
        fout.write(b'\x00' * pad_bytes_per_stream)  # pad with zeros
        print(f"Padded stream {i+1}/{num_streams}")

print(f"Padded file created: {output_path}")
print(f"New size should be: {num_streams * target_bytes_per_stream} bytes")