import socket
import heapq
from collections import defaultdict
import pickle


class HuffmanNode:
    """Node of a Huffman tree, holds info on it's left and right node as well as the char and its frequency in the msg"""
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    # basically the same thing as compareTo in java, used for heaps
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(text):
    """Auxiliary function, makes a dict of elements and their frequencies"""
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1
    return frequency


def build_huffman_tree(frequency: defaultdict):
    """Uses a heap to look through every node, needs a frequency table to work"""
    priority_queue = []
    for char, freq in frequency.items():
        # Creating "leaf" nodes for the tree
        node = HuffmanNode(char=char, freq=freq)
        heapq.heappush(priority_queue, node)

    # For every leaf node and the ones that are being created
    while len(priority_queue) > 1:
        # left are the smaller ones
        left = heapq.heappop(priority_queue)
        # right are the bigger or the same ones in terms of frequency
        right = heapq.heappop(priority_queue)
        # creating the "branch node" of the tree and adding it onto the heap
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(priority_queue, merged)

    # Returns the root of the tree
    return heapq.heappop(priority_queue)


def build_codebook(root: HuffmanNode, current_code="", codebook=None):
    """Actually a recursive function, builds a codebook used for encoding, has the frequencies as bits"""
    if codebook is None:
        codebook = {}

    if root is None:
        return codebook

    # If current node is a char node (has the frequency of the given char)
    if root.char is not None:
        # Jeśli tylko jeden znak, przypisz "0" jako domyślny kod
        codebook[root.char] = current_code if current_code != "" else "0"
        return codebook

    # left is 0, right is 1 for the navigation in the Huffman's tree
    build_codebook(root.left, current_code + "0", codebook)
    build_codebook(root.right, current_code + "1", codebook)

    return codebook


def huffman_encode(text):
    """Returns a string of bits and the Huffman's tree."""
    if not text:
        return "", None

    # self-explanatory really, just check the functions above
    frequency = build_frequency_table(text)
    huffman_tree = build_huffman_tree(frequency)
    codebook = build_codebook(huffman_tree)

    # converts every char into the navigation version from the codebook
    encoded_text = ''.join([codebook[char] for char in text])
    return encoded_text, huffman_tree


def main():
    HOST = '192.168.118.53'
    PORT = 65432

    try:
        with open('input.txt', 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print("Plik input.txt nie istnieje!")
        return

    # Kodowanie Huffmana
    encoded_text, huffman_tree = huffman_encode(text)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(10)
            s.connect((HOST, PORT))
            # Serializacja i wysyłka słownika Huffmana
            serialized_dict = pickle.dumps(huffman_tree)
            dict_length = len(serialized_dict)
            s.sendall(str(dict_length).encode('utf-8').zfill(16))
            s.sendall(serialized_dict)
            # Wysłanie długości i zakodowanego tekstu jako bajty
            length = len(encoded_text)
            s.sendall(str(length).encode('utf-8').zfill(16))
            s.sendall(encoded_text.encode('ascii'))  # ascii, bo jeżeli kompresować, to na pełnej
            print("Tekst został wysłany do serwera.")
        except socket.timeout:
            print("Timeout: Serwer nie odpowiedział w ciągu 10 sekund.")
        except socket.error as e:
            print(f"Błąd sieciowy: {e}")
        except Exception as e:
            print(f"Inny błąd: {e}")


if __name__ == "__main__":
    main()