import socket
import pickle

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def huffman_decode(encoded_text, huffman_tree):
    """Works around the tree, goes through every node until it finds a character node. Simple, really."""
    if not encoded_text:
        return ""

    current_node = huffman_tree
    decoded_text = []

    for bit in encoded_text:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right

        # if the node is a "leaf", get the char and go through the next ones from the root
        if current_node.char is not None:
            decoded_text.append(current_node.char)
            current_node = huffman_tree

    return ''.join(decoded_text)


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
                    # Odbiór długości słownika, zawsze 16 bo tak wysyła to klient
                    tree_length_data = conn.recv(16).decode('utf-8')
                    tree_length = int(tree_length_data)
                    # Odbiór słownika
                    tree_data = b""
                    while len(tree_data) < tree_length:
                        # użyte min, żeby przypadkowo bufora nie wypełnić danymi, które nie należą do drzewa
                        data = conn.recv(min(1024, tree_length - len(tree_data)))
                        if not data:
                            break
                        tree_data += data
                    huffman_tree = pickle.loads(tree_data)

                    # Odbiór długości zakodowanego tekstu, zawsze 16 bo tak wysyła to klient
                    length_data = conn.recv(16).decode('utf-8')
                    length = int(length_data)
                    # Odbiór zakodowanego tekstu jako bajty
                    encoded_data = b""
                    while len(encoded_data) < length:
                        # same case co w przypadku drzewa, ale raczej tutaj dałoby się obyć bez (z reguły tekst jest ostatni w wiadomości)
                        data = conn.recv(min(1024, length - len(encoded_data)))
                        if not data:
                            break
                        encoded_data += data
                    encoded_text = encoded_data.decode('ascii')  # Dekodowanie z ascii, bo tak klient wysyła wiadomość

                    # Dekodowanie
                    decoded_text = huffman_decode(encoded_text, huffman_tree)

                    # Zapis do pliku
                    with open('output.txt', 'w', encoding='utf-8') as file:
                        file.write(decoded_text)
                    print("Tekst został zdekodowany i zapisany do output.txt")
                except Exception as e:
                    print(f"Wystąpił błąd: {e}")


if __name__ == "__main__":
    main()