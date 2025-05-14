import socket
import heapq
from collections import defaultdict
import pickle


def build_huffman_tree(text):
    """Buduje drzewo Huffmana na podstawie częstotliwości znaków."""
    freq = defaultdict(int)
    for char in text:
        freq[char] += 1

    heap = [[weight, [char, ""]] for char, weight in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    return sorted(heap[0][1:], key=lambda p: (len(p[-1]), p))


def encode_huffman(text):
    """Koduje tekst za pomocą kodowania Huffmana."""
    if not text:
        return "", {}

    huffman_tree = build_huffman_tree(text)
    huffman_dict = {char: code for char, code in huffman_tree}

    encoded = "".join(huffman_dict[char] for char in text)
    return encoded, huffman_dict


def main():
    HOST = '192.168.1.100'
    PORT = 65432

    try:
        with open('input.txt', 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print("Plik input.txt nie istnieje!")
        return

    # Kodowanie Huffmana
    encoded_text, huffman_dict = encode_huffman(text)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(10)
            s.connect((HOST, PORT))
            # Serializacja i wysyłka słownika Huffmana
            serialized_dict = pickle.dumps(huffman_dict)
            dict_length = len(serialized_dict)
            s.sendall(str(dict_length).encode('utf-8').zfill(16))
            s.sendall(serialized_dict)
            # Wysłanie długości i zakodowanego tekstu
            length = len(encoded_text)
            s.sendall(str(length).encode('utf-8').zfill(16))
            s.sendall(encoded_text.encode('utf-8'))
            print("Tekst został wysłany do serwera.")
        except socket.timeout:
            print("Timeout: Serwer nie odpowiedział w ciągu 10 sekund.")
        except socket.error as e:
            print(f"Błąd sieciowy: {e}")
        except Exception as e:
            print(f"Inny błąd: {e}")


if __name__ == "__main__":
    main()