import numpy as np
from itertools import combinations

# Macierz Hamminga spełniająca wymagania do korekcji dwóch błędów (min odległość 5 między słowami kodowymi)
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

bin_to_dec = [128, 64, 32, 16, 8, 4, 2, 1]

def kodowanie(tekst):
    wynik = []
    for znak in tekst:
        bity_danych = []
        for bit in format(ord(znak), '08b'): # zamiana liter na indeks z ASCII po czym na liczbę binarną
            bity_danych.append(int(bit))
        bity_parzystosci = (np.dot(H[:, :8], bity_danych) % 2).tolist() # (polowa Hamminga * bity) modulo 2 każdego elementu
        wynik.append(bity_danych + bity_parzystosci) # połączone wektory danych i parzystosci dodajemy do wynikowej macierzy
    return wynik

def sprawdz_poprawnosc(wiadomosc):
    odkodowana = []
    for slowo in wiadomosc:
        syndrom = np.dot(H, slowo) % 2
        if not any(syndrom): # jezeli wszystkie wyrazy w syndromie == 0 to w słowie nie ma błędów
            odkodowana.append(slowo)
            continue

        # szukanie jednego błędu
        znaleziony = False
        for i in range(len(H[0])): # dla każdej kolumny
            if np.array_equal(H[:, i], syndrom): # jeżeli kolumna jest równa syndromowi, to i jest indeksem błędu
                slowo[i] = 1 - slowo[i]
                znaleziony = True # ustawiamy flagę żeby nie szukać dwóch błędów
                break

        #szukanie dwóch błędów
        if not znaleziony:
            for i, j in combinations(range(len(H[0])), 2): # dla różnych kombinacji dwóch indeksow
                suma_kolumn = (H[:, i] + H[:, j]) % 2 # sumujemy dwie kolumny
                if np.array_equal(suma_kolumn, syndrom): # jeżeli syndrom jest równy sumie kolumny to znalezliśmy błędy
                    slowo[i] = 1 - slowo[i]
                    slowo[j] = 1 - slowo[j]
                    break

        odkodowana.append(slowo)
    return odkodowana

def dekodowanie(odkodowana):
    tekst = ''
    for slowo in odkodowana:
        number = 0
        for bit_index in range(8): # dla pierwszych 8 bitów słowa
            number += slowo[bit_index] * bin_to_dec[bit_index] # konwertujemy binarne wartości na decymalne
        tekst += chr(number) # dodajemy literę do tekstu wynikowego
    return tekst