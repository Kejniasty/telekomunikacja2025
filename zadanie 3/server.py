import socket
import pickle


def decode_huffman(encoded_text, huffman_dict):
    """Dekoduje tekst zakodowany metodą Huffmana."""
    reverse_dict = {code: char for char, code in huffman_dict.items()}
    decoded = ""
    current_code = ""

    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_dict:
            decoded += reverse_dict[current_code]
            current_code = ""

    return decoded


def main():
    HOST = '0.0.0.0'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Serwer nasłuchuje na {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Połączono z {addr}")
                try:
                    # Odbiór długości słownika
                    dict_length_data = conn.recv(16).decode('utf-8')
                    dict_length = int(dict_length_data)
                    # Odbiór słownika
                    dict_data = b""
                    while len(dict_data) < dict_length:
                        data = conn.recv(1024)
                        if not data:
                            break
                        dict_data += data
                    huffman_dict = pickle.loads(dict_data)

                    # Odbiór długości zakodowanego tekstu
                    length_data = conn.recv(16).decode('utf-8')
                    length = int(length_data)
                    # Odbiór zakodowanego tekstu
                    encoded_text = ""
                    while len(encoded_text) < length:
                        data = conn.recv(1024).decode('utf-8')
                        if not data:
                            break
                        encoded_text += data

                    # Dekodowanie
                    decoded_text = decode_huffman(encoded_text, huffman_dict)

                    # Zapis do pliku
                    with open('output.txt', 'w', encoding='utf-8') as file:
                        file.write(decoded_text)
                    print("Tekst został zdekodowany i zapisany do output.txt")
                except Exception as e:
                    print(f"Wystąpił błąd: {e}")


if __name__ == "__main__":
    main()