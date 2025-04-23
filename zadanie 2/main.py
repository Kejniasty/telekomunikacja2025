import serial
import time
import sys

# control characters (in hex)
SOH = b"\x01"       # start of header
EOT = b"\x04"       # end of transmission
ACK = b"\x06"       # positive acknowledgment
NAK = b"\x15"       # negative acknowledgment
CAN = b"\x18"       # cancel transmission
CHAR_C = b"C"       # for CRC mode
BLOCK_SIZE = 128
DEBUG_FLAG = 0

def debug(*args, **kwargs):
    # simple debug print function triggered by global flag
    if DEBUG_FLAG == 1:
        print(*args, **kwargs)

def use_crc():
    crc_mode = input("Use CRC mode? [yes/no]: ").strip().lower()
    if crc_mode in ["y", "yes"]:
        print("CRC mode selected")
        return True
    else:
        print("Checksum mode selected")
        return False

def calculate_checksum(block):
    # one-byte checksum (mod 256) for the block
    return sum(block) % 256

def calculate_crc(data):
    # calculate 16-bit CRC for the block
    crc = 0
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def pad_data(data):
    # pad block to 128 bytes with CTRL-Z (0x1A)
    padding = b"\x1A"
    length = len(data)
    if length < BLOCK_SIZE:
        data += padding * (BLOCK_SIZE - length)
    return data

def split_into_blocks(message):
    # splits message into 128-byte blocks
    blocks = []
    for i in range(0, len(message), BLOCK_SIZE):
        block = message[i:i+BLOCK_SIZE]
        block = pad_data(block)
        blocks.append(block)
    debug(blocks)
    return blocks

def send_message(port, message, use_crc=True, timeout=10):
    # send message via XModem
    message_bytes = message.encode("utf-8")
    blocks = split_into_blocks(message_bytes)

    print("Waiting for receiver initiation signal ('C' or 'NAK')...")
    start = time.time()
    start_char = None

    while time.time() - start < 60:
        if port.in_waiting > 0:
            ch = port.read(1)
            if ch in [NAK, CHAR_C]:
                start_char = ch
                break
        time.sleep(1)

    if start_char is None:
        print("Timeout! No response from receiver within 60 seconds.")
        return False

    print("Received initiation signal from receiver:", start_char)

    block_num = 1
    for block in blocks:
        retries = 0
        while retries < 10:
            block_num_byte = bytes([block_num & 0xFF])
            complement = bytes([(255 - block_num) & 0xFF])
            header = SOH + block_num_byte + complement

            if use_crc:
                crc_val = calculate_crc(block)
                error_check = crc_val.to_bytes(2, byteorder="big")
            else:
                checksum_val = calculate_checksum(block)
                error_check = bytes([checksum_val])

            packet = header + block + error_check
            print(f"Sending block: {block_num}, attempt: {retries + 1}...")
            port.write(packet)

            start = time.time()
            response = None

            while time.time() - start < timeout:
                if port.in_waiting > 0:
                    response = port.read(1)
                    break
                time.sleep(0.1)

            if response == ACK:
                print(f"Block {block_num} sent successfully")
                block_num += 1
                break
            elif response == NAK:
                print(f"Block {block_num} failed, retrying ({retries + 1})...")
                retries += 1
            else:
                print(f"Block {block_num}: no valid response, retrying ({retries + 1})...")
                retries += 1
        else:
            print(f"Failed to send block {block_num} after {retries} attempts.")
            return False

    retries = 0
    while retries < 10:
        port.write(EOT)
        start = time.time()
        response = None
        while time.time() - start < timeout:
            if port.in_waiting > 0:
                response = port.read(1)
                if response == ACK:
                    print("Receiver confirmed end of communication.")
                    return
            time.sleep(0.1)
        retries += 1
    print("Receiver did not confirm end of communication.")

def receive_message(port, use_crc=True, timeout=10):
    # receive message via XModem
    init_char = CHAR_C if use_crc else NAK

    print("Starting transfer. Sending initiation character:", init_char)
    start = time.time()

    while time.time() - start < 60:
        port.write(init_char)
        time.sleep(10)
        if port.in_waiting > 0:
            break

    start = time.time()
    header = None
    while time.time() - start < timeout:
        if port.in_waiting > 0:
            response_char = port.read(1)
            if response_char == SOH:
                debug("Received SOH from sender!")
                header = response_char
                break
        time.sleep(0.1)

    if header is None:
        print("Failed to receive packet.")
        return False

    block_num = port.read(1)[0]
    block_num_comp = port.read(1)[0]

    if (block_num + block_num_comp) & 0xFF != 0xFF:
        debug(f"block_num={block_num}\nblock_num_comp={block_num_comp}")
        print("Invalid block number.")
        port.write(NAK)
        return False

    data = port.read(BLOCK_SIZE)
    if len(data) != BLOCK_SIZE:
        print("Invalid block size received!")
        port.write(NAK)
        return False

    if use_crc:
        check_bytes = port.read(2)
        received_check = int.from_bytes(check_bytes, byteorder="big")
        calculated_check = calculate_crc(data)
    else:
        check_bytes = port.read(1)
        received_check = check_bytes[0]
        calculated_check = calculate_checksum(data)

    if received_check != calculated_check:
        print(f"Error check failed:\nExpected {calculated_check}\nReceived {received_check}")
        port.write(NAK)
        return False
    else:
        port.write(ACK)
        message = data.rstrip(b"\x1A")
        try:
            message.decode("utf-8")
        except UnicodeDecodeError:
            message.decode("utf-8", errors="replace")
        print(f"Message received successfully: '{message}'")
        return True

# main
if __name__ == "__main__":
    port_name = ""
    while not port_name[:3] == "COM":
        port_name = input("Enter serial port (e.g., COM10): ").strip().upper()

    try:
        baudrate = int(input("Enter baudrate (default 9600): ").strip())
    except ValueError:
        baudrate = 9600
        print(f"Invalid value. Using default baudrate={baudrate}")

    try:
        ser = serial.Serial(port_name, baudrate, timeout=10)
    except Exception as e:
        print("Failed to open serial port:", e)
        sys.exit(1)

    while True:
        print("--------------\nMain Menu:\n"
              "1. Send message\n"
              "2. Receive message\n"
              "3. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            use_crc_mode = use_crc()
            msg = input("Enter message to send: ")
            debug(f"use_crc: {use_crc_mode}\nmessage: '{msg}'")
            send_message(ser, msg, use_crc=use_crc_mode)

        elif choice == "2":
            use_crc_mode = use_crc()
            debug(f"use_crc: {use_crc_mode}")
            receive_message(ser, use_crc=use_crc_mode)

        elif choice == "3":
            break
        else:
            print("Invalid option selected!")

    ser.close()
    input("Press Enter to exit.")
