import numpy as np

H = np.array([
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]
], dtype=int)

def kodowanie(tekst):
    wynik = []
    for znak in tekst:
        bity_danych = [int(bit) for bit in format(ord(znak), '08b')]
        bity_parzystosci = (np.dot(H[:, :8], bity_danych) % 2).tolist()
        wynik.append(bity_danych + bity_parzystosci)
    return wynik

def sprawdz_poprawnosc(wiadomosc):
    odkodowana = []
    for slowo in wiadomosc:
        syndrom = np.dot(H, slowo) % 2
        if any(syndrom):
            for i in range(len(H[0])):
                if np.array_equal(H[:, i], syndrom):
                    slowo[i] = 1 - slowo[i]
                    break
        odkodowana.append(slowo)
    return odkodowana

def dekodowanie(odkodowana):
    tekst = ''
    for slowo in odkodowana:
        number = 0
        for bit_index in range(7, -1, -1):
            number += slowo[7 - bit_index] * 2**bit_index
        tekst += chr(number)

    return tekst

tekst = "ABCD"
print(tekst)

zakodowana = kodowanie(tekst)
print(zakodowana)

zakodowana[2][6] = 1 - zakodowana[2][6]
print(zakodowana)

poprawiona = sprawdz_poprawnosc(zakodowana)
print(poprawiona)

tekst_po_korekcie = dekodowanie(poprawiona)
print(tekst_po_korekcie)
