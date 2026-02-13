class CeaserCipher:
    def __init__(self):
        self._alphabet = [
        "A", "B", "C", "D", "E", "F", "G",
        "H", "I", "J", "K", "L", "M", "N",
        "O", "P", "Q", "R", "S", "T", "U",
        "V", "W", "X", "Y", "Z"
        ]
        
        self.english_freq = {
        'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
        'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
        'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
        'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
        'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
        }
        
    def moved_alphabet_left(self, n):
        moved_alphabet = []
        for i in range(len(self._alphabet)):
            moved_alphabet.append(self._alphabet[i-n])
        return moved_alphabet
    
    def moved_alphabet_right(self, n):
        moved_alphabet = []
        for i in range(len(self._alphabet)):
            moved_alphabet.append(self._alphabet[(i+n)%26])
        return moved_alphabet
    
    def encrypt_text(self, text, moved_alphabet):
        encrypted_text = ""
        for chr in text:
            new_char=chr
            if chr in self._alphabet:
                current_index = self._alphabet.index(chr)
                new_char = moved_alphabet[current_index]
            encrypted_text+=new_char
        return encrypted_text
    
    def decrypt_text(self, encrypted_text, moved_alphabet):
        decrypted_text = ""
        for chr in encrypted_text:
            new_char = chr
            if chr in moved_alphabet:
                current_index = moved_alphabet.index(chr)
                new_char = self._alphabet[current_index]
            decrypted_text+=new_char
        return decrypted_text
    
    def brute_force(self, encrypted_text):
        for i in range(len(self._alphabet)):
            moved_alphabet = self.moved_alphabet_left(i)
            decrypted_text = self.decrypt_text(encrypted_text, moved_alphabet)
            check = str(input(f"Is {decrypted_text} correct? Y/n "))
            if check == "Y" or check == "y":
                return
            elif check == "N" or check == "n":
                continue
            else:
                print("Invalid input")
    
    def count_text_frequencies(self, text):
        counts = {char: 0 for char in self._alphabet}
        total_count = 0
        for ch in text:
            if ch in self._alphabet:
                counts[ch] += 1
                total_count += 1
        
        for key, value in counts.items():
            counts[key] = value * (100/total_count) if total_count > 0 else 0
        return counts
    
    def partial_crypto_analysis(self, encrypted_text):
        results = []
        aplhabet_index = {c:i for i,c in enumerate(self._alphabet)}
        for shift in range(26):
            decrypted_text = ""
            for char in encrypted_text.upper():
                if char in aplhabet_index:
                    idx = (aplhabet_index[char] - shift)%26
                    decrypted_text += self._alphabet[idx]
                else:
                    decrypted_text += char
            freq = self.count_text_frequencies(decrypted_text)
            score = self.chi_squared(freq)
            results.append((shift, score, decrypted_text))

        results.sort(key=lambda x: x[1])
        print("Top 5 most likely decryptions: \n")
        for i, (shiftf, scoref, decrypted_textf) in enumerate(results[:5], 1):
            print(f"{i}. Shift={shiftf}, Score={scoref:.2f}")
            print(f"   {decrypted_textf[:80]}...\n")
            
        return results[0][2]
        
        
    def chi_squared(self, observed_frequencies):
        expected = self.english_freq
        itera = [((observed_frequencies[k]-expected[k])**2)/expected[k] for k in expected]
        chi2 = sum(itera)
        return chi2        
    
    
        
if __name__ == "__main__":
    key = 25
    encryptor = CeaserCipher()
    
    # Тестовое сообщение
    plaintext = """
        What is Lorem Ipsum?`
        Lorem Ipsum is simply dummy text of the 
        printing and typesetting industry. Lorem 
        Ipsum has been the industry's standard dummy
        text ever since the 1500s, when an unknown
        printer took a galley of type and scrambled 
        it to make a type specimen book. It has
        survived not only five centuries, but als
        o the leap into electronic typesetting, re
        maining essentially unchanged. It was popula
        rised in the 1960s with the release of Letraset   
    """
    
    # Шифруем текст с заданным сдвигом
    moved_alphabet = encryptor.moved_alphabet_left(key)
    encrypted_text = encryptor.encrypt_text(plaintext.upper(), moved_alphabet)
    print(f"Encrypted text: {encrypted_text}\n")
    
    # # Brute-force с ручной проверкой
    # print("Brute-force decryption (manual check):")
    # encryptor.brute_force(encrypted_text)
    
    # Автоматическое взлом с chi-squared
    print("\nAutomatic crack using chi-squared:")
    decrypted_text = encryptor.partial_crypto_analysis(encrypted_text)
    print(f"Most likely decryption: {decrypted_text}")
    