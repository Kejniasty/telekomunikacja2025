import socket

def decode_text(binary):
    """Dekoduje ciąg bitowy na tekst."""
    text = ""
    # Przetwarzanie ciągu bitowego po 8 bitów
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:  # Upewniamy się, że mamy pełny bajt
            # Zamiana 8-bitowego ciągu na znak ASCII
            char_code = int(byte, 2)
            text += chr(char_code)
    return text

def main():
    # Dane serwera
    HOST = '0.0.0.0'  # Adres serwera
    PORT = 65432        # Port do komunikacji

    # Inicjalizacja serwera
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Serwer nasłuchuje na {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Połączono z {addr}")
                try:
                    # Odbiór długości wiadomości
                    length_data = conn.recv(16).decode('utf-8')
                    if not length_data:
                        continue
                    length = int(length_data)
                    
                    # Odbiór zakodowanego tekstu
                    encoded_text = ""
                    while len(encoded_text) < length:
                        data = conn.recv(1024).decode('utf-8')
                        if not data:
                            break
                        encoded_text += data

                    # Dekodowanie tekstu
                    decoded_text = decode_text(encoded_text)

                    # Zapis do pliku
                    with open('output.txt', 'w', encoding='utf-8') as file:
                        file.write(decoded_text)
                    print("Tekst został zdekodowany i zapisany do output.txt")
                except Exception as e:
                    print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    main()