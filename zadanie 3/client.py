import socket

def encode_text(text):
    """Koduje tekst na ciąg bitowy (8 bitów na znak)."""
    binary = ""
    for char in text:
        # Zamiana znaku na kod ASCII i na 8-bitowy ciąg binarny
        binary += format(ord(char), '08b')
    return binary

def main():
    # Dane serwera
    HOST = '192.168.18.37'  # Adres serwera (localhost dla testów)
    PORT = 65432        # Port do komunikacji

    # Odczyt pliku wejściowego
    try:
        with open('input.txt', 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print("Plik input.txt nie istnieje!")
        return

    # Kodowanie tekstu
    encoded_text = encode_text(text)
    
    # Nawiązanie połączenia z serwerem
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            # Wysłanie długości wiadomości (aby serwer wiedział, ile danych odbierać)
            length = len(encoded_text)
            s.sendall(str(length).encode('utf-8').zfill(16))  # Długość z paddingiem do 16 bajtów
            # Wysłanie zakodowanego tekstu
            s.sendall(encoded_text.encode('utf-8'))
            print("Tekst został wysłany do serwera.")
        except ConnectionRefusedError:
            print("Nie można połączyć się z serwerem!")
        except Exception as e:
            print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    main()