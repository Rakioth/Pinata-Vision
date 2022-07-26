import re
import sys

# Decode a barcode associated with a Piñata Vision (PV) Card

# Version 1.01  05JUN2022   Rakioth

# More details about the barcode can be found at:
# http://pinataisland.info/viva/Pinata_Vision_barcode

# Data encoded within the barcode is obfuscated using three techniques/steps:

# 1. Shuffling (rearranging the order of bits), using a shuffle table
# 2. Negation (inverting various bits), using XOR with a bitmask
# 3. Logical transformation, using AND, OR, XOR on groups of 4 bits

# Each barcode row is individually obfuscated (based on its check digit),
# so there are 16 variations on how a row's bits can get obscured.

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

# Unobfuscate a barcode row and return its encoded data

def unobfuscate_row(row):

    # A barcode row consists of 15 digits (60 bits) of obfuscated data,
    # followed by a 16th (4 bit) check digit.

    if len(row) != 16:
        sys.exit("Bad row length")

    # Determine the specific obfuscation used (based on the check digit)
    # Convert the check digit from hex to decimal, for use as an array index

    index = int(row[-1], 16)

    # Deobfuscation involves applying a logical transformation, negating
    # various bits, then (re)shuffling them (back into their proper order)

    # First, perform a logical translation on each hex nibble (4 bits)

    # (Since the result of a translation is known [based on each possible
    # input], we can skip the actual logical operations and directly
    # transform each translated value back to its original input value)

    # print(f"Obfuscated = {row}")

    row_value = row.translate(row.maketrans("76543210EFABCD98", "0123456789ABCDEF"))

    # print(f"Negated = {row_value}")

    # Next, pack the row's hex string as a 64-bit value, XOR it with the
    # correct negate mask, then unpack it as a binary string for unshuffling

    bytes1 = bytes.fromhex(row_value)         # XOR Barcode row (as 64-bit int)
    bytes2 = bytes.fromhex(negate[index])     # With negate mask (as 64-bit int)

    xor_bytes = bytes([b1 ^ b2 for b1, b2 in zip(bytes1, bytes2)])
    xor_hex = xor_bytes.hex()
    xor_bin = format(int(xor_hex, 16), "064b")

    # Last, unshuffle the bits to get back to the original encoded data

    # (Ignore the check digit, and only unshuffle the first 60 bits)

    encoded_data = ""

    for x in range(60):
        encoded_data += xor_bin[shuffle[index][x]]

    # print(f"Encoded = {encoded_data}")

    # Encoded data is now unobfuscated

    return encoded_data

# Decode a PV card's encoded data into human-readable format

# Data is preceded by a 5-bit payload type (identifying the type of data that follows)

#   +---------+---------+----
#   |Type|Data|Type|Data| ...
#   +---------+---------+----

def decode_data(encoded_data):

    raw = encoded_data      # Encoded binary data

    offset = 0              # Current offset within encoded data

    end_of_data = 0         # End of data flag.  Set if type:00000, data:0000 occurs

    payload_type = ""       # Current payload type

    payload_type_size = 5

    while not end_of_data:

        payload_type = raw[offset : offset + payload_type_size]
        offset += payload_type_size

        # Move on to a new card, if we've gotten out-of-sync and scanned past the end of the barcode
        if not payload_type:
            end_of_data = 1

        if payload_type == "00000":     # Start or end of encoded data.

            payload_00000_size = 4

            # 0000 is end of data.  0001 is start of data.
            # Payload data.  Type of data varies, based on the payload type

            payload_data = raw[offset : offset + payload_00000_size]
            offset += payload_00000_size

            if payload_data == "0000":
                end_of_data = 1
                print("00000/EndOfData")
            elif payload_data == "0001":
                # Start of data.  No-op
                print("00000/StartOfData", end=" ")
            else:
                print(f"Don't recognize type {payload_type} data: {payload_data}", end=" ")

        elif payload_type == "00001":   # ID

            payload_00001_size = 12

            payload_data = raw[offset : offset + payload_00001_size]
            offset += payload_00001_size

            print(f"00001/ID: {int(payload_data, 2)}", end=" ")

        elif payload_type == "00010":   # Trick stick reskin

            payload_00010_size = 12

            payload_data = raw[offset : offset + payload_00010_size]
            offset += payload_00010_size

            print(f"00010/TrickStick: {int(payload_data, 2)}", end=" ")

        elif payload_type == "00011":   # Starting date

            payload_00011_size = 12

            payload_data = raw[offset : offset + payload_00011_size]
            offset += payload_00011_size

            day = int(payload_data[0:5], 2)
            month = int(payload_data[5:9], 2)
            unknown = int(payload_data[9:12], 2)

            print(f"00011/StartDate: {month}/{day}", end=" ")

        elif payload_type == "00100":   # Ending date

            payload_00100_size = 12

            payload_data = raw[offset : offset + payload_00100_size]
            offset += payload_00100_size

            day = int(payload_data[0:5], 2)
            month = int(payload_data[5:9], 2)
            unknown = int(payload_data[9:12], 2)

            print(f"00100/EndDate: {month}/{day}", end=" ")

        elif payload_type == "00111":   # Name, variable length

            # The name is NUL-terminated.  The only way we can determine the payload length is by
            # reading 5 bits at a time, and checking for 00000 (NUL).

            name = ""                   # Piñata name
            payload_data = ""

            shift = 1                   # Capitalize the first letter, and any letter following a space

            # Read the first 5 bits, and increment the offset to prepare for reading the following character

            letter = raw[offset : offset + 5]
            offset += 5
            payload_data += letter

            while letter != "00000":    # While not NUL (end of name reached)...
                if letter == "00001":           # is it a space?  Append a space, and set the shift flag
                    name += " "
                    shift = 1
                else:
                    # a = "00010" = 2, so we need to subtract 1 before adding it to 64 (uppercase) or 96 (lowercase)
                    name += chr(int(letter, 2) - 1 + (64 if shift else 96))
                    shift = 0

                letter = raw[offset : offset + 5]
                offset += 5
                payload_data += letter

                # Handle case if we get out of sync and read past the end of the data
                if not letter:
                    letter = "00000"

            print(f"00111/Name: {name}", end=" ")

        elif payload_type == "01000":   # Gamertag identifier (hash?)

            payload_01000_size = 30

            payload_data = raw[offset : offset + payload_01000_size]
            offset += payload_01000_size

            # print(f"01000/Gamertag: {int(payload_data, 2)}", end=" ")
            print(f"01000/Gamertag: {payload_data}", end=" ")

        elif payload_type == "01001":   # Wildcard trait

            payload_01001_size = 2

            payload_data = raw[offset : offset + payload_01001_size]
            offset += payload_01001_size

            print(f"01001/Wildcard: {int(payload_data, 2)}", end=" ")

        elif payload_type == "01010":   # Variant color

            payload_01010_size = 4

            payload_data = raw[offset : offset + payload_01010_size]
            offset += payload_01010_size

            print(f"01010/Variant: {int(payload_data, 2)}", end=" ")

        elif payload_type == "01011":   # Size?

            payload_01011_size = 3

            payload_data = raw[offset : offset + payload_01011_size]
            offset += payload_01011_size

            # print(f"01011/Size: {int(payload_data, 2)}", end=" ")
            print(f"01011/Size: {payload_data}", end=" ")

        elif payload_type == "10000":   # SparseCallback

            payload_10000_size = 16

            payload_data = raw[offset : offset + payload_10000_size]
            offset += payload_10000_size

            # print(f"10000/Sparse: {int(payload_data, 2)}", end=" ")
            print(f"10000/Sparse: {payload_data}", end=" ")

        elif payload_type == "10001":   # Timewarp

            payload_10001_size = 4

            payload_data = raw[offset : offset + payload_10001_size]
            offset += payload_10001_size

            # print(f"10001/Timewarp: {int(payload_data, 2)}", end=" ")
            print(f"10001/Timewarp: {payload_data}", end=" ")

        elif payload_type == "10010":   # Weather type

            payload_10010_size = 3

            payload_data = raw[offset : offset + payload_10010_size]
            offset += payload_10010_size

            # print(f"10010/Weather: {int(payload_data, 2)}", end=" ")
            print(f"10010/Weather: {payload_data}", end=" ")

        elif payload_type == "10011":   # Weather duration

            payload_10011_size = 8

            payload_data = raw[offset : offset + payload_10011_size]
            offset += payload_10011_size

            # print(f"10011/Duration: {int(payload_data, 2)}", end=" ")
            print(f"10011/Duration: {payload_data}", end=" ")

        elif payload_type == "10100":   # ID (target) of Sparse callback

            payload_10100_size = 12

            payload_data = raw[offset : offset + payload_10100_size]
            offset += payload_10100_size

            print(f"10100/ID: {int(payload_data, 2)}", end=" ")

        elif payload_type == "10110":   # Reusability

            payload_10110_size = 5

            payload_data = raw[offset : offset + payload_10110_size]
            offset += payload_10110_size

            # print(f"10110/Reuse: {int(payload_data, 2)}", end=" ")
            print(f"10110/Reuse: {payload_data}", end=" ")

        elif payload_type == "11000":   # Use cost

            payload_11000_size = 10

            payload_data = raw[offset : offset + payload_11000_size]
            offset += payload_11000_size

            value = int(payload_data[0:7], 2)
            magnitude = int(payload_data[7:10], 2)

            cost = value * (10**magnitude)

            print(f"11000/UseCost: {cost}", end=" ")

        elif payload_type == "11010":   # Jukebox track?

            payload_11001_size = 4

            payload_data = raw[offset : offset + payload_11001_size]
            offset += payload_11001_size

            # print(f"11010/?: {int(payload_data, 2)}", end=" ")
            print(f"11010/?: {payload_data}", end=" ")

        elif payload_type == "11101":   # Accessories, variable length

            # Color count, n items with colors, count, m items

            # Get the count for any color accessories.  May be zero.

            color_count = raw[offset : offset + 4]
            offset += 4

            items = ""                  # Holds list of (human-readable) accessory values

            item_length = 8
            color_length = 4

            color_names = (
                "Default",      # 0, should never get used
                "Red",          # 1
                "Orange",       # 2
                "Yellow",       # 3
                "Brown",        # 4
                "Pink",         # 5
                "Purple",       # 6
                "Green",        # 7
                "Light Green",  # 8
                "Blue",         # 9
                "Cyan",         # 10
                "Violet",       # 11
                "Black",        # 12
                "White",        # 13
                "14",           # 14
                "15"            # 15
            )

            color_count = int(color_count, 2)   # Convert count from binary to decimal

            # Read that number of items and colors

            for i in range(color_count):

                # 8-bit item value, followed by 4-bit item color

                item = raw[offset : offset + item_length]
                offset += item_length

                item_color = raw[offset : offset + color_length]
                offset += color_length

                # Format item color as a color (or decimal value)

                item_color = int(item_color, 2)

                if len(color_names) > item_color:
                    # There's a known color for this value
                    item_color = color_names[item_color]

                # Append the data for human-readable parsing

                items += f"{item_color} {lookup_accessory_name_for_item(int(item, 2))}{(', ' if (i + 1 != color_count) else '')}"

            # Now repeat the process one more time, getting the count and list of (default color) items

            count = raw[offset : offset + 4]
            offset += 4

            count = int(count, 2)   # Convert count from binary to decimal

            # Append comma, if there were previous color accessories

            if color_count:
                items += (', ' if count else '')

            # Read that number of items

            for i in range(count):

                # 8-bit item values

                item = raw[offset : offset + item_length]
                offset += item_length

                # Append the data for human-readable parsing

                items += f"{lookup_accessory_name_for_item(int(item, 2))}{(', ' if (i + 1 != count) else '')}"

            total_count = color_count + count

            print(f"11101/Accessory: {total_count} item{('s ' if (total_count > 1) else ' ')}{items}", end=" ")

        else:
            print(f"Don't recognize this payload type: {payload_type}")

            end_of_data = 1     # Give up on this card

# Lookup accessory name for an accessory item value.

def lookup_accessory_name_for_item(item):

    names = (
        "",     # 0 no such accessory
        "Retro Disco Wig",
        "Breegull Carrier",
        "Shark Tooth Necklace",
        "Cool Shades",
        "Howdy Pardner Hat",
        "Doenut Stalker",
        "Inca Bracelet",
        "Fur Boots",
        "Fair Dinkum Hat",
        "King Tut's Hat",
        "Yokel Teeth",
        "Jurassic Hair",
        "Yee-Haw Hat",
        "Señor Sombrero",
        "Pillager's Helmet",
        "Thunder Cut",
        "Beanie Cap",
        "Weather-Girl Wig",
        "Diggerling Helmet Mk1",
        "Gas Mask",
        "Party Horns",
        "Kazooie Talons",
        "Caterpillars",
        "Yee-Haw Spurs",
        "Super Hero Mask",
        "School Cap",
        "Baseball Cap",
        "Yee-Haw Saddle",
        "Tiara of Tranquility",
        "Slim Tache",
        "Spiked Collar",
        "Geek Glasses",
        "Reporter's Camera",
        "Bling Teeth",
        "Bow",
        "Fez",
        "Fake Winner's Rosette",
        "Diamond Choker",
        "Blackeye Patch",
        "Tap Shoes",
        "Ballet Shoes",
        "Crown",
        "Handlebar Mustache",
        "Football Helmet",
        "Sweaty Wrist Band",
        "Bling Bangle",
        "Beaded Wig",
        "Rashberry Badge",
        "Secret Agent Bowtie",
        "Bling Bracelet",
        "Crystal Broach",
        "Bunnycomb Ears",
        "Bushy Mustache",
        "Soupswill Cook Hat",
        "The Von Ghoul",
        "Yee-Haw Boots",
        "Butcha's",
        "Diamond Necklace",
        "Combat Boots",
        "Pegasus Wings",
        "Romance Earrings",
        "Mermaid Earrings",
        "Big Bling Earrings",
        "Silver Medal",
        "Big Jolly Lips",
        "Comedian\s Nose",
        "Buck Teeth",
        "Gold Medal",
        "Soccer Boots",
        "Squazzil Hat",
        "DanceGlow",
        "Pendant Necklace",
        "Halo of Hardness",
        "Safety Helmet",
        "Sweaty Head Band",
        "Breegull Waders",
        "Bronze Medal",
        "Leafos Medallion",
        "Baby's Bib",
        "Toff Monocle",
        "Astro-Walkers",
        "Halloween Bolts",
        "Bling Nose-Ring",
        "Dellmonty",
        "Traditional Watch",
        "Mermaid Necklace",
        "Eighties Watch",
        "Tussle Tricorn",
        "Rashberry Hat",
        "Rashberry Helmet",
        "Reading Glasses",
        "Red Nose",
        "Robber's Mask",
        "Extreme Sports Goggles",
        "Santa Hat",
        "Non-Resident Scarf",
        "Sea-Shell Collar",
        "Bunnycomb Slippers",
        "Snow Shoes",
        "Belly-Splash Specials",
        "Granny's Tache",
        "Funky Tie",
        "Conga's Top Hat",
        "Breegull Turbo Trainers",
        "Ga-Ga Necklace",
        "Dastardos Scarf",
        "Bell",
        "Bonnet",
        "Buzzlegum Keeper Hat",
        "Buttercup Hair Flower",
        "Daisy Hair Flower",
        "Bling Earrings",
        "Not-so-Bling Earrings",
        "Pendant Earrings",
        "Pearly Bracelet",
        "Poppy Hair Flower",
        "Barkbark Tags",
        "Sunflower Hair Flower",
        "Student's Hat",
        "Comedian's Choice",
        "Strong 'n' Macho",
        "Cook Hat",
        "Tail Bow",
        "Super Hero Belt",
        "Fruity Hat",
        "Mr. Pants Hat",
        "Sailor Hat",
        "Conkerific Helmet",
        "Vela Wig",
        "Juno Helmet",
        "Grunty Hat",
        "Jam-Jars Hat",
        "Binner's Hat",
        "Princess Hat",
        "Von Ghoul Helmet",
        "Saberman Helmet",
        "Ortho's Spare Hat",
        "Knight Helmet",
        "Headphones",
        "Jiggy Earrings",
        "Lupus Ears",
        "Disco Shades",
        "Flying Goggles",
        "Bottles' Glasses",
        "Romantic Flower",
        "Battletoad Bracelets",
        "Prisoner Bracelet",
        "Sheriff's Badge",
        "Clockwork Key",
        "Kameo Wings",
        "Fake Fin",
        "Flamenco Shoes",
        "Ash Slippers",
        "Cleopatra's Necklace",
        "Stethoscope",
        "Star Earrings",
        "Furry Earmuffs",
        "Lucky Earrings",
        "Harlequin Mask",
        "Ponocky Club Hat",
        "Camo Cap",
        "Apples and Pears Hat",
        "Chewnicorn Horn",
        "Firefighter's Hat",
        "Nurse's Hat",
        "Golden Necklace",
        "Edo Wig",
        "Pointed Hat",
        "Comrade's Hat",
        "Dentures Of The Night",
        "Turkish Slippers",
        "Bullfighter's Hat",
        "Caesar's Hat",
        "Clogs",
        "Homburg",
        "Safari Hat",
        "La Parisienne",
        "Yeoman's Helm",
        "Hula Necklace",
        "Mountie Hat",
        "Tribal Mask",
        "Liberty Crown",
        "Jokduri",
    )

    if len(names) > item:
        return names[item]
    else:
        return "Unknown"

# Read a (tab-delimited) list of barcodes (and PV card filenames) from STDIN

# A list of barcodes can be found online at:
# http://pinataisland.info/viva/Pinata_Vision_barcode/List_of_barcodes

with open("barcodes.txt", "r") as f:

    line = f.readline()
    sys.stdout = open("decoded.txt", "w")

    while line:

        pinata_card = re.split("\t", line.strip())

        # Extract a barcode and (optional) tab-delimited filename

        barcode = pinata_card[0]                # 16-digit (per row) barcode; rows delimited by space
        filename = pinata_card[1]               # Filename of PV card corresponding to this barcode

        # Split a space-delimited (multiple row) barcode into separate rows

        rows = re.split(" ", barcode)

        # Unobfuscate each row into a single record of encoded data

        encoded_data = ""     # Concatenated rows of unobfuscated data

        for row in rows:

            # Append this row's encoded data

            encoded_data += unobfuscate_row(row)

        # Handle human-readable display of encoded data
        # print(f"{filename} ->", end=" ")
        # decode_data(encoded_data)

        print(f"{encoded_data}\t{filename}")
        line = f.readline()

    sys.stdout.close()
