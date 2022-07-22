import re
import sys
import json
from textwrap import wrap
from dataclasses import dataclass

shuffle = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,),
    (0, 30, 1, 31, 2, 32, 3, 33, 4, 34, 5, 35, 6, 36, 7, 37, 8, 38, 9, 39, 10, 40, 11, 41, 12, 42, 13, 43, 14, 44, 15, 45, 16, 46, 17, 47, 18, 48, 19, 49, 20, 50, 21, 51, 22, 52, 23, 53, 24, 54, 25, 55, 26, 56, 27, 57, 28, 58, 29, 59,),
    (0, 20, 40, 1, 21, 41, 2, 22, 42, 3, 23, 43, 4, 24, 44, 5, 25, 45, 6, 26, 46, 7, 27, 47, 8, 28, 48, 9, 29, 49, 10, 30, 50, 11, 31, 51, 12, 32, 52, 13, 33, 53, 14, 34, 54, 15, 35, 55, 16, 36, 56, 17, 37, 57, 18, 38, 58, 19, 39, 59,),
    (0, 12, 24, 36, 48, 1, 13, 25, 37, 49, 2, 14, 26, 38, 50, 3, 15, 27, 39, 51, 4, 16, 28, 40, 52, 5, 17, 29, 41, 53, 6, 18, 30, 42, 54, 7, 19, 31, 43, 55, 8, 20, 32, 44, 56, 9, 21, 33, 45, 57, 10, 22, 34, 46, 58, 11, 23, 35, 47, 59,),
    (0, 9, 18, 27, 36, 44, 52, 1, 10, 19, 28, 37, 45, 53, 2, 11, 20, 29, 38, 46, 54, 3, 12, 21, 30, 39, 47, 55, 4, 13, 22, 31, 40, 48, 56, 5, 14, 23, 32, 41, 49, 57, 6, 15, 24, 33, 42, 50, 58, 7, 16, 25, 34, 43, 51, 59, 8, 17, 26, 35,),
    (0, 7, 14, 21, 28, 35, 42, 48, 54, 1, 8, 15, 22, 29, 36, 43, 49, 55, 2, 9, 16, 23, 30, 37, 44, 50, 56, 3, 10, 17, 24, 31, 38, 45, 51, 57, 4, 11, 18, 25, 32, 39, 46, 52, 58, 5, 12, 19, 26, 33, 40, 47, 53, 59, 6, 13, 20, 27, 34, 41,),
    (0, 6, 12, 18, 24, 30, 35, 40, 45, 50, 55, 1, 7, 13, 19, 25, 31, 36, 41, 46, 51, 56, 2, 8, 14, 20, 26, 32, 37, 42, 47, 52, 57, 3, 9, 15, 21, 27, 33, 38, 43, 48, 53, 58, 4, 10, 16, 22, 28, 34, 39, 44, 49, 54, 59, 5, 11, 17, 23, 29,),
    (0, 5, 10, 15, 20, 25, 30, 35, 40, 44, 48, 52, 56, 1, 6, 11, 16, 21, 26, 31, 36, 41, 45, 49, 53, 57, 2, 7, 12, 17, 22, 27, 32, 37, 42, 46, 50, 54, 58, 3, 8, 13, 18, 23, 28, 33, 38, 43, 47, 51, 55, 59, 4, 9, 14, 19, 24, 29, 34, 39,),
    (0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 39, 42, 45, 48, 51, 54, 57, 1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 40, 43, 46, 49, 52, 55, 58, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 41, 44, 47, 50, 53, 56, 59, 3, 7, 11, 15, 19, 23, 27, 31, 35,),
    (0, 4, 8, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 1, 5, 9, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55, 58, 2, 6, 10, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 56, 59, 3, 7, 11,),
    (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 59, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57,),
    (0, 3, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 1, 4, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 2, 5,),
    (0, 3, 6, 9, 12, 15, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 1, 4, 7, 10, 13, 16, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 2, 5, 8, 11, 14, 17,),
    (0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 44, 46, 48, 50, 52, 54, 56, 58, 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 45, 47, 49, 51, 53, 55, 57, 59, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41,),
    (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41,),
    (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45,),
)

negate = (
    "878F0B496878F0B0",
    "9607CF2B59607CF0",
    "A59E03CD2A59E030",
    "B416C7AF1B416C70",
    "C3AD1A41EC3AD1B0",
    "D225DE23DD225DF0",
    "E1BC12C5AE1BC130",
    "F034D6A79F034D70",
    "F0B496878F0B4970",
    "E13C52E5BE13C530",
    "A59E03CD2A59E030",
    "B416C7AF1B416C70",
    "C32D5A61FC32D5B0",
    "D2A59E03CD2A59F0",
    "878F0B496878F0B0",
    "9607CF2B59607CF0",
)


@dataclass
class PinataCard:
    id: str
    variant: str
    wildcard: str
    name: str
    type: str

    def __post_init__(self):
        with open(f"assets/data/pinata.json") as json_file:
            data = json.load(json_file)
            pinata_data = data[self.id]
            self.id = pinata_data[self.type]
            self.variant = pinata_data["variants"].get(self.variant)
            self.wildcard = pinata_data["wildcards"].get(self.wildcard)
            self.name = (
                "".join(format(ord(c) + 1, "0b")[2:] for c in self.name)
                if self.name
                else None
            )


@dataclass
class WeatherCard:
    id: str
    duration: str
    type: str = "weather"

    def __post_init__(self):
        with open(f"assets/data/{self.type}.json") as json_file:
            data = json.load(json_file)
            self.id = data["weathers"].get(self.id)
            self.duration = data["duration"].get(self.duration)


@dataclass
class TypeCard:
    id: str
    type: str

    def __post_init__(self):
        with open(f"assets/data/{self.type}.json") as json_file:
            data = json.load(json_file)
            self.id = data[self.id]


def check_digit(data):

    obfuscation_set = {
        0: "0",
        1: "1",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "D",
        11: "C",
        12: "B",
        13: "A",
        14: "F",
        15: "E",
    }
    row_hex = format(int(data, 2), "015X")
    weight = 3
    checksum = 0

    for c in row_hex:
        checksum += int(c, 16) * weight
        weight = 4 - weight

    for x in range(16):
        if (checksum + x) % 16 == 0:
            return obfuscation_set[x]


def obfuscate_row(row):

    check = check_digit(row)
    index = int(check, 16)
    xor_bin = [None] * 60

    for x in range(60):
        xor_bin[shuffle[index][x]] = row[x]

    check = format(
        int(
            check.translate(
                check.maketrans("76543210EFABCD98", "0123456789ABCDEF")
            ),
            16,
        ),
        "04b",
    )

    xor_hex = format(int("".join(xor_bin) + check, 2), "016X")
    bytes_xor = bytes.fromhex(xor_hex)
    bytes_negate = bytes.fromhex(negate[index])
    bytes_barcode = bytes([b1 ^ b2 for b1, b2 in zip(bytes_xor, bytes_negate)])
    row_value = bytes_barcode.hex().upper()

    return row_value.translate(
        row_value.maketrans("0123456789ABCDEF", "76543210EFABCD98")
    )


def encode_data(decoded_data):

    encoded_data = "0000000011011000000"
    barcode_data = ""

    if decoded_data.type == "pinata" or decoded_data.type == "egg":
        encoded_data += f"00001{decoded_data.id}"
        if decoded_data.name:
            encoded_data += f"00111{decoded_data.name}00000"
        if decoded_data.wildcard:
            encoded_data += f"01001{decoded_data.wildcard}"
        if decoded_data.variant:
            encoded_data += f"01010{decoded_data.variant}"

    elif decoded_data.type == "weather":
        encoded_data += f"10011{decoded_data.duration}"
        encoded_data += f"10010{decoded_data.id}"

    elif decoded_data.type == "timewarp":
        encoded_data += f"10001{decoded_data.id}"

    elif decoded_data.type == "trick-stick":
        encoded_data += f"00010{decoded_data.id}"

    elif decoded_data.type == "terrain":
        encoded_data += f"10000{decoded_data.id}"

    else:
        encoded_data += f"00001{decoded_data.id}"

    encoded_data += f"000000000"

    for x in range(60, 241, 60):
        if len(encoded_data) < x:
            encoded_data = encoded_data.ljust(x, "0")
            break

    for row in wrap(encoded_data, 60):
        barcode_data += obfuscate_row(row)

    return barcode_data


def unicode_barcode(decoded_data):

    unicode_data = ""
    wrapper = wrap(decoded_data, 113)

    for x in reversed(range(len(wrapper))):
        unicode_data += wrapper[x].replace("0", " ").replace("1", "█") + "\n"

    return unicode_data


def generate_card(card):

    bar_pattern = {
        "0": "1110010",
        "1": "1100110",
        "2": "1101100",
        "3": "1000010",
        "4": "1011100",
        "5": "1001110",
        "6": "1010000",
        "7": "1000100",
        "8": "1001000",
        "9": "1110100",
        "A": "1011000",
        "B": "1001100",
        "C": "1100100",
        "D": "1101000",
        "E": "1100010",
        "F": "1000110",
    }
    decoded_data = ""

    for row in wrap(encode_data(card), 16):
        for c in row:
            decoded_data += bar_pattern[c]
        decoded_data += "1"

    return unicode_barcode(decoded_data)


def main():
    with open("decoded.txt", "r") as f:

        line = f.readline()
        sys.stdout = open("encoded.txt", "w")

        while line:

            pinata_card = re.split("\t", line.strip())

            barcode = pinata_card[0]
            filename = pinata_card[1]

            decoded_data = ""

            for row in wrap(barcode, 60):
                decoded_data += obfuscate_row(row) + " "

            print(f"{decoded_data[0:-1]}\t{filename}")
            line = f.readline()

        sys.stdout.close()


def test():
    pinata_test = PinataCard("S'morepion", "White (In-Game)", "Large Claw", "Stingy", "pinata")
    print(pinata_test)
    print(generate_card(pinata_test))

    egg_test = PinataCard("Buzzenge", "Black", "Hooked Beak", "", "egg")
    print(egg_test)
    print(generate_card(egg_test))

    home_test = PinataCard("Chippopotamus", "", "", "", "home")
    print(home_test)
    print(generate_card(home_test))

    sweet_test = PinataCard("Arocknid", "", "", "", "sweet")
    print(sweet_test)
    print(generate_card(sweet_test))

    weather_test = WeatherCard("Stormy", "1 Hour")
    print(weather_test)
    print(generate_card(weather_test))

    fruit_test = TypeCard("Blackberry", "fruit")
    print(fruit_test)
    print(generate_card(fruit_test))

    timewarp_test = TypeCard("Midday", "timewarp")
    print(timewarp_test)
    print(generate_card(timewarp_test))

    trickstick_test = TypeCard("Sausage", "trick-stick")
    print(trickstick_test)
    print(generate_card(trickstick_test))

    terrain_test = TypeCard("Sand", "terrain")
    print(terrain_test)
    print(generate_card(terrain_test))


if __name__ == "__main__":
    main()
    # test()
