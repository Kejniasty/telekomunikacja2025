import serial
import time
import sys

# thanks to all involved, you are amazing <3
# LC

# Global variables
BLOCK_SIZE = 128 # default size of data block used in the packet in bytes
BAUDRATE = 9600 # data transfer rate in bits per second, used for the serial port opening
TIMEOUT = 10 # default timeout time in seconds
CTRL_Z = b"\x1A"

# control characters (in hex)
SOH = b"\x01"       # start of header
EOT = b"\x04"       # end of transmission
ACK = b"\x06"       # positive acknowledgment
NAK = b"\x15"       # negative acknowledgment
ETB = b"\x17"       # end of transsmision block (not really used, defined in the XModem Protocol with CRC site)
CAN = b"\x18"       # cancel transmission
CHAR_C = b"C"       # for CRC mode


def read_from_file(name: str) -> str:
    """Auxiliary function, returns file's contents"""
    with open(name, "r") as file:
        message = file.read()
    return message


def write_to_file(name: str, message: bytes):
    """Auxiliary function that writes a message to a file"""
    with open(name, 'wb') as file:
        file.write(message)
    return


def calculate_checksum(block):
    """One-byte checksum (mod 256) for the block, used for the basic checksum variant"""
    return sum(block) % 256


def calculate_crc(data):
    """Calculating a 16-bit CRC for the block, used with CRC variant"""
    crc = 0
    # For every byte in a data block (typically 128 bytes)
    for byte in data:
        # xor 8 left shifted byte (gives a 16 bit output)
        crc ^= (byte << 8)
        for _ in range(8):
            # Check if the most significant bit is 1
            if crc & 0x8000:
                # If it is, we left shift crc once, xor it with the generator polynomial (XModem standard)
                # and the result with 16 bits of 1's
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                # If not, left shift it once and the result with 16 bits 1's
                crc = (crc << 1) & 0xFFFF
    return crc


def pad_data(data):
    """Auxiliary function that pads a data block to 128 bytes with CTRL-Z (0x1A)"""
    padding = CTRL_Z
    length = len(data)
    # Check if data block's length is lower than earlier set max block's size
    if length < BLOCK_SIZE:
        data += padding * (BLOCK_SIZE - length)
    return data


def split_into_blocks(message):
    """Auxiliary function that splits message into 128-byte blocks"""
    blocks = []
    for i in range(0, len(message), BLOCK_SIZE):
        block = message[i:i+BLOCK_SIZE]
        block = pad_data(block)
        blocks.append(block)
    return blocks


def send_message(port: serial.Serial, message, use_crc=False):
    """Sending message via XModem. Every packet of main communication has a format of
    "(SOH flag)[block_number][not(block_number)][128-byte data block][CRC sum/control sum]" """
    # Using UTF-8 for encoding (no polish letters :( )
    message_bytes = message.encode("utf-8")
    # Splitting data into blocks
    blocks = split_into_blocks(message_bytes)

    print("Waiting for receiver initiation signal ('C' or 'NAK')...")
    start = time.time()
    start_char = None

    # waiting max 60 seconds
    while time.time() - start < 60:
        # If there are any bytes waiting in the port's buffer
        if port.in_waiting > 0:
            # we read that little bastard and save it in a variable
            ch = port.read(1)
            # it should be a NAK or C flag (specifies which version of data verification is going to be used)
            if ch in [NAK, CHAR_C]:
                start_char = ch
                break
        time.sleep(1)

    # if we hadn't received anything, we abort the process
    if start_char is None:
        print("Timeout! No response from receiver within 60 seconds.")
        return False

    print("Received initiation signal from receiver:", start_char)

    block_num = 1
    for block in blocks:
        retries = 0
        # retrying max of 10 times
        while retries < 10:
            # calculating the block number
            block_num_byte = bytes([block_num & 0xFF])
            # calculating the complement of the block number
            complement = bytes([(255 - block_num) & 0xFF])
            # lastly compiling them all into the header of the packet
            header = SOH + block_num_byte + complement

            # calculating the checksum
            if use_crc:
                crc_val = calculate_crc(block)
                checksum = crc_val.to_bytes(2, byteorder="big")
            else:
                checksum_val = calculate_checksum(block)
                checksum = bytes([checksum_val])

            packet = header + block + checksum
            print(f"Sending block: {block_num}, attempt: {retries + 1}...")
            port.write(packet)

            start = time.time()
            response = None
            # After sending the packet we wait for a response
            while time.time() - start < TIMEOUT:
                if port.in_waiting > 0:
                    response = port.read(1)
                    break
                time.sleep(0.1)

            if response == ACK:
                # If it's ACK, we continue
                print(f"Block {block_num} sent successfully")
                block_num += 1
                break
            elif response == NAK:
                # If it's NAK, we try sending the packet again after recompiling it
                print(f"Block {block_num} failed, retrying ({retries + 1})...")
                retries += 1
            else:
                # If it's none, we also try resending the recompiled packet
                print(f"Block {block_num}: no valid response, retrying ({retries + 1})...")
                retries += 1
        else:
            # If the block isn't sent, we abort the process
            print(f"Failed to send block {block_num} after {retries} attempts.")
            return False

    # Now we're trying to end the transmission in a valid way
    retries = 0
    while retries < 10:
        # We send EOT flag
        port.write(EOT)
        start = time.time()
        while time.time() - start < TIMEOUT:
            # If there is something in the port's buffer we read it
            if port.in_waiting > 0:
                response = port.read(1)
                # and if it's ACK flag, we can end the communication
                if response == ACK:
                    print("Receiver confirmed end of communication.")
                    return
            time.sleep(0.1)
        retries += 1
    # Edge case if the receiver didn't acknowledge the EOT
    print("Receiver did not confirm end of communication.")


def receive_message(port: serial.Serial, use_crc=False):
    """Receiving a message via XModem. Every packet of main communication has a format of
    "(SOH flag)[block_number][not(block_number)][128-byte data block][CRC sum/control sum]" """

    # we set the first flag for the type of checksum
    if use_crc:
        init_char = CHAR_C
    else:
        init_char = NAK

    print("Starting transfer. Sending initiation character:", init_char)
    start = time.time()

    while time.time() - start < 60:
        # We send the checksum variant flag (C or NAK)
        port.write(init_char)
        time.sleep(10)
        if port.in_waiting > 0:
            break

    start = time.time()
    header = None
    while time.time() - start < TIMEOUT:
        # First we wait for the SOH flag
        if port.in_waiting > 0:
            response_char = port.read(1)
            if response_char == SOH:
                header = response_char
                break
        time.sleep(0.1)

    # If we didn't receive SOH we abort the process
    if header is None:
        print("Failed to receive packet.")
        return False

    # now we read the block number and its compliment
    block_num = port.read(1)[0]
    block_num_comp = port.read(1)[0]

    # if it doesn't sum to all 1's in a byte, it means that something went wrong
    if (block_num + block_num_comp) & 0xFF != 0xFF:
        print("Invalid block number.")
        # we send NAK to tell the sender something went wrong in the packet
        port.write(NAK)
        # and abort the process
        return False

    # we read the data block (128 bytes)
    data = port.read(BLOCK_SIZE)
    # if it's length isn't the right size we send NAK and abort the process
    if len(data) != BLOCK_SIZE:
        print("Invalid block size received!")
        port.write(NAK)
        return False

    # now we calculate the right checksum and read the checksum from the packet
    if use_crc:
        check_bytes = port.read(2)
        received_check = int.from_bytes(check_bytes, byteorder="big")
        calculated_check = calculate_crc(data)
    else:
        check_bytes = port.read(1)
        received_check = check_bytes[0]
        calculated_check = calculate_checksum(data)

    # if the packet's checksum doesn't match up we abort the process (bytes got corrupted), after sending NAK
    if received_check != calculated_check:
        print(f"Error check failed:\nExpected {calculated_check}\nReceived {received_check}")
        port.write(NAK)
        return False
    else:
        # if it's alright, we send an ACK and add the block to the final message, after decoding it of course
        port.write(ACK)
        # we strip the message of ctrl-z's that are used for the padding
        message = data.rstrip(CTRL_Z)
        try:
            message.decode("utf-8")
        except UnicodeDecodeError:
            message.decode("utf-8", errors="replace")
        print(f"Message received successfully: '{message}'")

        return message


def do_crc():
    """Auxiliary function, basically converts a string to a boolean"""
    crc_mode = input("Use CRC mode? [yes/no]: ").strip().lower()
    if crc_mode in {"y", "yes"}:
        print("CRC mode selected")
        return True
    else:
        print("Checksum mode selected")
        return False

if __name__ == "__main__":
    # there is no point of me commenting the main function so hf it's not really that complicated
    port_name = ""
    while not port_name[:3] == "COM":
        port_name = input("Enter serial port (e.g., COM10):\n> ").strip().upper()
    try:
        ser = serial.Serial(port_name, BAUDRATE, timeout=10)
    except Exception as e:
        print("Failed to open serial port:", e)
        sys.exit(1)

    while True:
        choice = input("--------------\n"
              "1. Send message\n"
              "2. Receive message\n"
              "3. Exit\n> ").strip()
        match choice:
            case "1":
                use_crc_mode = do_crc()
                mode = None
                while mode not in {"1", "2"}:
                    mode = input("Choose the source of the message:\n"
                                 "1. From file\n"
                                 "2. From keyboard\n> ").strip()
                match mode:
                    case "1":
                        name = input("Enter the file's name:\n> ")
                        msg = read_from_file(name)
                    case "2":
                        msg = input("Enter message to send:\n> ")
                    case _:
                        print("no clue how you landed here, here have a break")
                        break
                send_message(ser, msg, use_crc=use_crc_mode)

            case "2":
                use_crc_mode = do_crc()
                mode = input("Should the message be saved in a file? [y/n]\n> ").strip().lower()
                name = None
                if mode in {"y", "yes"}:
                    name = input("Enter the file's name:\n> ")
                msg = receive_message(ser, use_crc=use_crc_mode)
                if name is not None:
                    write_to_file(name, msg)

            case "3":
                break
            case _:
                print("Invalid option selected!")

    ser.close()
    input("Press Enter to exit.")
