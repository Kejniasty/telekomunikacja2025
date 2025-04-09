import error_correction as ec
import random
# TODO: wrzucenie bledu w randomowym bicie

# mode - a = kodowanie, b = dekodowanie, c = kodowanie -> dekodowanie
def file_handling(input_name: str, output_name: str, mode='a', check_errors='a') -> None:
    match mode:
        case 'a':
            with open(input_name, 'r') as input_file:
                encoded = []
                for line in input_file:
                    print(line, end='')
                    encoded += ec.kodowanie(line)
                print()

                error_byte = random.randint(0, len(encoded))
                error_bit = random.randint(0, 7)
                print(f"Ups! na {error_bit + 1} bicie {error_byte + 1} bajtu wkradł się błąd!")

                encoded[error_byte][error_bit] = 1 - encoded[error_byte][error_bit]

                temp_string = ''
                for word in encoded:
                    for bit in word:
                        temp_string += str(bit)
                    temp_string += ' '
                encoded.append(temp_string)


            with open(output_name, 'w') as output_file:
                output_file.write(temp_string)

        case 'b':
            with open(input_name, 'r') as input_file:
                line = input_file.readline()
                line = line.strip('\n')
                line = line.split(' ')
                encoded = []
                for i in range(len(line)):
                    encoded.append([])
                    for bit in line[i]:
                        encoded[i].append(int(bit))
                if check_errors == 'a':
                    encoded = ec.sprawdz_poprawnosc(encoded)
                text = ec.dekodowanie(encoded)

            with open(output_name, 'w') as output_file:
                print(text)
                output_file.write(text)

        case 'c':
            encoded_file = []
            with open(input_name, 'r') as input_file:
                for line in input_file:
                    print(line, end='')
                    encoded_file += ec.kodowanie(line)
            print()

            error_byte = random.randint(0, len(encoded_file))
            error_bit = random.randint(0, 7)
            print(f"Ups! na {error_bit + 1} bicie {error_byte + 1} bajtu wkradł się błąd!")

            encoded_file[error_byte][error_bit] = 1 - encoded_file[error_byte][error_bit]

            temp_string = ''
            for word in encoded_file:
                for bit in word:
                    temp_string += str(bit)
                temp_string += ' '
            print(temp_string, end='\n')

            if check_errors == 'a':
                encoded_file = ec.sprawdz_poprawnosc(encoded_file)
            text = ec.dekodowanie(encoded_file)

            with open(output_name, 'w') as output_file:
                print(text)
                output_file.write(text)




# mode - a = kodowanie, b = dekodowanie, c = kodowanie -> dekodowanie
def keyboard_handling(text, mode='a', check_errors='a'):
    match mode:
        case 'a':
            encoded_line = ec.kodowanie(text)

            error_byte = random.randint(0, len(encoded_line))
            error_bit = random.randint(0, 7)
            print(f"Ups! na {error_bit + 1} bicie {error_byte + 1} bajtu wkradł się błąd!")

            temp_string = ''
            for word in encoded_line:
                for bit in word:
                    temp_string += str(bit)
                temp_string += ' '
            print(temp_string)

        case 'b':
            line = text.strip('\n')
            line = line.split(' ')
            encoded = []
            for i in range(len(line)):
                encoded.append([])
                for bit in line[i]:
                    encoded[i].append(int(bit))
            if check_errors == 'a':
                encoded = ec.sprawdz_poprawnosc(encoded)
            text = ec.dekodowanie(encoded)
            print(text)

        case 'c':
            encoded_line = ec.kodowanie(text)
            error_byte = random.randint(0, len(encoded_line))
            error_bit = random.randint(0, 7)
            print(f"Ups! na {error_bit + 1} bicie {error_byte + 1} bajtu wkradł się błąd!")
            temp_string = ''
            for word in encoded_line:
                for bit in word:
                    temp_string += str(bit)
                temp_string += ' '
            print(temp_string, end='\n')
            if check_errors == 'a':
                encoded_line = ec.sprawdz_poprawnosc(encoded_line)
            text = ec.dekodowanie(encoded_line)
            print(text)



if __name__ == "__main__":
    encode = input("a. Koduj\nb. Dekoduj\nc. Pełny cykl (Koduj->Dekoduj):\n> ")

    input_mode = input("a. Wczytaj z pliku\nb. Wpisz z klawiatury:\n> ")
    match input_mode:
        case 'a':
            input_name = input("Plik wejściowy:\n> ")
            output_name = input("Plik wyjściowy:\n> ")
            match encode:
                case 'a':
                    file_handling(input_name, output_name, encode)
                case 'b':
                    check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                    file_handling(input_name, output_name, encode, check_error_flag)
                case 'c':
                    check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                    file_handling(input_name, output_name, encode, check_error_flag)
                case _:
                    print("Zła opcja wybrana")
        case 'b':
            text = input("Wprowadź dowolny tekst:\n> ")
            match encode:
                case 'a':
                    keyboard_handling(text, encode)
                case 'b':
                    check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                    keyboard_handling(text, encode, check_error_flag)
                case 'c':
                    check_error_flag = input("a. Sprawdź i popraw błędy\nb. Nie sprawdzaj błędów:\n> ")
                    keyboard_handling(text, encode, check_error_flag)
                case _:
                    print("zła opcja wybrana")
