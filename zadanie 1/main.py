import error_correction as ec
import random

# funkcja do konwersji macierzy 2D na string
def make_string(matrix):
    temp_string = ''
    for word in matrix:
        for bit in word:
            temp_string += str(bit)
        temp_string += ' '
    return temp_string

# mode - a = kodowanie, b = dekodowanie, c = kodowanie -> dekodowanie
def file_handling(input_name: str, output_name: str, errors: int, mode='a', check_errors='a') -> None:
    match mode:
        # kodowanie tekstu z pliku do pliku
        case 'a':
            with open(input_name, 'r') as input_file:
                encoded = []
                print("===================\nOdczytana wiadomość\n===================")
                for line in input_file:
                    print(line, end='')
                    encoded += ec.kodowanie(line) # do macierzy dodajemy kolejne zakodowane linie
                print()

            #losujemy w którym słowie wystąpi błąd i zależnie od wybranej ilości błędów psujemy "errors" bitów
            error_byte = random.randint(0, len(encoded))
            for i in range(errors):
                error_bit = random.randint(0, 15)
                encoded[error_byte][error_bit] = 1 - encoded[error_byte][error_bit]
                print(f"Ups! na {16 - error_bit} bicie {error_byte + 1} słowa wkradł się błąd!")

            # zamieniamy macierz z błędem na stringa
            temp_string = make_string(encoded)
            print("====================\nZakodowana wiadomość\n====================")
            print(temp_string)

            # którego wpisujemy do pliku
            with open(output_name, 'w') as output_file:
                output_file.write(temp_string)

        # dekodowanie z pliku do pliku
        case 'b':
            # w pliku słowa są oddzielone spacjami, dlatego korzystamy ze .split()
            with open(input_name, 'r') as input_file:
                line = input_file.readline()
            line = line.strip('\n')
            line = line.split(' ')
            # konwertujemy poszczególne bity macierzy na liczby całkowite
            encoded = []
            for i in range(len(line)):
                encoded.append([])
                for bit in line[i]:
                    encoded[i].append(int(bit))
            if check_errors == 'a':
                # korygujemy błędy w macierzy
                encoded = ec.sprawdz_poprawnosc(encoded)
                print("====================\nWiadomość bez błędu\n====================")
                print(make_string(encoded))
            # dekodujemy macierz
            text = ec.dekodowanie(encoded)

            with open(output_name, 'w') as output_file:
                print("===================\nOdczytana wiadomość\n===================")
                print(text)
                # wpisujemy ją do pliku
                output_file.write(text)

        # kodowanie, dekodowanie i zapis tego do pliku
        case 'c':
            print("===================\nOdczytana wiadomość\n===================")
            # odczytujemy zawartość pliku i kodujemy go linia po linii
            encoded_file = []
            with open(input_name, 'r') as input_file:
                for line in input_file:
                    print(line, end='')
                    # dodajemy każdą linię do macierzy
                    encoded_file += ec.kodowanie(line)
            print()

            # w wylosowanym słowie psujemy macierz
            error_byte = random.randint(0, len(encoded_file))
            for i in range(errors):
                error_bit = random.randint(0, 15)
                encoded_file[error_byte][error_bit] = 1 - encoded_file[error_byte][error_bit]
                print(f"Ups! na {16 - error_bit} bicie {error_byte + 1} słowa wkradł się błąd!")


            print("====================\nZakodowana wiadomość\n====================")
            # zamieniamy macierz na string, żeby ją wyświetlić w ładnej formie
            temp_string = make_string(encoded_file)
            print(temp_string)

            if check_errors == 'a':
                # korygujemy błędy w macierzy
                encoded_file = ec.sprawdz_poprawnosc(encoded_file)
                print("====================\nWiadomość bez błędu\n====================")
                print(make_string(encoded_file))
            # macierz dekodujemy
            text = ec.dekodowanie(encoded_file)

            print("====================\nOdkodowana wiadomość\n====================")
            with open(output_name, 'w') as output_file:
                print(text)
                # zdekodowany tekst wpisujemy do pliku
                output_file.write(text)




# mode - a = kodowanie, b = dekodowanie, c = kodowanie -> dekodowanie
def keyboard_handling(text, errors, mode='a', check_errors='a'):
    match mode:
        # kodowanie tekstu z klawiatury na ekran
        case 'a':
            # kodujemy linię tekstu
            encoded_line = ec.kodowanie(text)

            # w wylosowanym słowie psujemy macierz
            error_byte = random.randint(0, len(encoded_line))
            for i in range(errors):
                error_bit = random.randint(0, 15)
                encoded_line[error_byte][error_bit] = 1 - encoded_line[error_byte][error_bit]
                print(f"Ups! na {16 - error_bit} bicie {error_byte + 1} słowa wkradł się błąd!")

            # zamieniamy macierz na tekst i wyświetlamy ją na ekranie
            temp_string = make_string(encoded_line)
            print("====================\nZakodowana wiadomość\n====================")
            print(temp_string)

        # dekodowanie tekstu z klawiatury na ekran
        case 'b':
            line = text.strip('\n')
            line = line.split(' ')
            # konwetujemy stringa na macierz intów
            encoded = []
            for i in range(len(line)):
                encoded.append([])
                for bit in line[i]:
                    encoded[i].append(int(bit))

            if check_errors == 'a':
                # korygujemy błędy w macierzy
                encoded = ec.sprawdz_poprawnosc(encoded)
                print("====================\nWiadomość bez błędu\n====================")
                print(make_string(encoded))

            # dekodujemy tekst i wyświetlamy go na ekranie
            text = ec.dekodowanie(encoded)
            print("====================\nOdkodowana wiadomość\n====================")
            print(text)

        # kodowanie + dekodowanie tekstu z klawiatury na ekran
        case 'c':
            # kodujemy tekst od użytkownika
            encoded_line = ec.kodowanie(text)

            # psujemy macierz w losowym słowie "errors" razy
            error_byte = random.randint(0, len(encoded_line))
            for i in range(errors):
                error_bit = random.randint(0, 15)
                encoded_line[error_byte][error_bit] = 1 - encoded_line[error_byte][error_bit]
                print(f"Ups! na {16 - error_bit} bicie {error_byte + 1} słowa wkradł się błąd!")

            # wyświetlamy zakodowaną wiadomość
            print("====================\nZakodowana wiadomość\n====================")
            print(make_string(encoded_line))

            if check_errors == 'a':
                # korygujemy błędy w macierzy
                encoded_line = ec.sprawdz_poprawnosc(encoded_line)
                print("====================\nWiadomość bez błędu\n====================")
                print(make_string(encoded_line))

            # dekodujemy macierz i wyświetlamy ją na ekranie
            text = ec.dekodowanie(encoded_line)
            print("====================\nOdkodowana wiadomość\n====================")
            print(text)



if __name__ == "__main__":
    while True:
        encode = input("a. Koduj\nb. Dekoduj\nc. Pełny cykl (Koduj->Dekoduj):\nd. Wyjście> ")

        input_mode = input("a. Wczytaj z pliku\nb. Wpisz z klawiatury:\n> ")
        match input_mode:
            case 'a':
                input_name = input("Plik wejściowy:\n> ")
                output_name = input("Plik wyjściowy:\n> ")
                match encode:
                    case 'a':
                        error_num = int(input("Wprowadź liczbę błędów do jednego bajtów wiadomości:\n> "))
                        file_handling(input_name, output_name, error_num, encode)
                    case 'b':
                        check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                        file_handling(input_name, output_name, 1, encode, check_error_flag)
                    case 'c':
                        error_num = int(input("Wprowadź liczbę błędów do jednego bajtów wiadomości:\n> "))
                        check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                        file_handling(input_name, output_name, error_num, encode, check_error_flag)
                    case _:
                        break
            case 'b':
                text = input("Wprowadź dowolny tekst:\n> ")
                match encode:
                    case 'a':
                        error_num = int(input("Wprowadź liczbę błędów do jednego bajtów wiadomości:\n> "))
                        keyboard_handling(text, error_num, encode)
                    case 'b':
                        check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                        keyboard_handling(text, 1, encode, check_error_flag)
                    case 'c':
                        error_num = int(input("Wprowadź liczbę błędów do jednego z bajtów wiadomości:\n> "))
                        check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                        keyboard_handling(text, error_num, encode, check_error_flag)
                    case _:
                        break
            case _:
                break
