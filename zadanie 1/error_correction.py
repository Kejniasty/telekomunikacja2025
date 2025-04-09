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
        bity_danych = []
        for bit in format(ord(znak), '08b'):
            bity_danych.append(int(bit))
        bity_parzystosci = (np.dot(H[:, :8], bity_danych) % 2).tolist() # (polowa Hamminga * bity) modulo 2 każdego elementu
        wynik.append(bity_danych + bity_parzystosci)
    return wynik

def sprawdz_poprawnosc(wiadomosc):
    odkodowana = []
    for bajt in wiadomosc:
        syndrom = np.dot(H, bajt) % 2
        if any(syndrom):
            for i in range(len(H[0])):
                if np.array_equal(H[:, i], syndrom):
                    bajt[i] = 1 - bajt[i]
                    break
        odkodowana.append(bajt)
    return odkodowana

def dekodowanie(odkodowana):
    tekst = ''
    for slowo in odkodowana:
        number = 0
        for bit_index in range(7, -1, -1):
            number += slowo[7 - bit_index] * 2**bit_index
        tekst += chr(number)

    return tekst
