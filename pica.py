import sys
import math
from tqdm import tqdm
from PIL import Image
import argparse
from pathlib import Path


def string_to_binary(s):
    return ''.join(format(byte, '08b') for byte in s.encode('utf-8'))


def binary_to_string(binary_str):
    # Ensure the binary string length is a multiple of 8
    if len(binary_str) % 8 != 0:
        raise ValueError("Binary string length must be a multiple of 8")

    byte_array = bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))

    return byte_array.decode('utf-8')


if __name__ == '__main__':
    sys.stderr.write(
        "\n"
        "   Powered by TwinIsland (twisland@outlook.com)\n"
        "   This software is for PRIVATE USE ONLY.\n"
        "   If you have obtained it unintentionally, please do not distribute it.\n"
        "\n"
    )

    parser = argparse.ArgumentParser(description="Encrypt/decrypt text into/from an image.")
    parser.add_argument("-i", "--image", required=True, help="Path to the image file")
    parser.add_argument("-e", "--encrypt", nargs="?", const=True,
                        help="Encrypt text into the image (optional input text)")
    parser.add_argument("-d", "--decrypt", action="store_true", help="Decrypt text from the image")

    args = parser.parse_args()

    get_meta_len = lambda _img_size: int(math.ceil(math.log2(_img_size)))

    if args.encrypt and args.decrypt:
        parser.error("You can only choose one mode: either encrypt (-e) or decrypt (-d).")

    if args.encrypt:
        if args.encrypt is True:  # No direct argument given, read from stdin
            text = sys.stdin.read().strip()
        else:
            text = args.encrypt

        if not text:
            parser.error("No input text provided for encryption. Use -e '<text>' or pipe input.")

        btext = string_to_binary(text)
        img = Image.open(args.image)
        pixels = img.load()
        img_size = img.size[0] * img.size[1]
        btext_len = len(btext)

        assert img_size >= btext_len, print("Image too small, text overflow")

        meta_len = get_meta_len(img_size)
        meta = bin(btext_len)[2:].zfill(meta_len)

        safe_iter = lambda arr, idx, default: arr[idx] if idx < len(arr) else default


        def round_bit(target, bit):
            if bit == 1:
                if target % 2 == 0:
                    target += 1
            else:
                if target % 2 != 0:
                    target -= 1
            return target


        pbar = None
        pbar_init, encrypt_done = False, False

        for y in range(img.size[0]):
            for x in range(img.size[1]):
                pix_idx = y * img.size[1] + x

                if pix_idx < meta_len:
                    r, g, b = pixels[y, x]
                    pixels[y, x] = (r, g, round_bit(b, int(meta[pix_idx])))
                    continue

                if not pbar_init:
                    sys.stderr.write(f"total bit: {btext_len}\n")
                    pbar = tqdm(total=btext_len, desc="start decrypt")
                    pbar_init = True

                if pix_idx >= btext_len + meta_len:
                    encrypt_done = True
                    break

                r, g, b = pixels[y, x]
                pixels[y, x] = (r, g, round_bit(b, int(safe_iter(btext, pix_idx - meta_len, 0))))
                pbar.update(1)

            if encrypt_done:
                break

        if pbar:
            tqdm.close(pbar)

        original_name = Path(args.image).stem
        img.save(f"encrypt_{original_name}.png")

        print(f"btext: {len(btext)}"
              f"\nsave to: encrypt_{original_name}.png"
              f"\ndone!")

    elif args.decrypt:
        img = Image.open(args.image)
        pixels = img.load()
        img_size = img.size[0] * img.size[1]

        btext = ""
        meta = ""
        btext_len = img_size
        meta_len = get_meta_len(img_size)
        pbar = None
        pbar_init, decrypt_done = False, False

        # Progress bar
        for y in range(img.size[0]):
            for x in range(img.size[1]):
                pix_idx = y * img.size[1] + x

                if pix_idx < meta_len:
                    # reading metadata
                    meta += str(pixels[y, x][2] % 2)
                    if pix_idx == meta_len - 1:
                        btext_len = int(meta, 2)
                else:
                    # reading bits
                    if pix_idx >= btext_len + meta_len:
                        decrypt_done = True
                        break

                    if not pbar_init:
                        sys.stderr.write(f"total bit: {btext_len}\n")
                        pbar = tqdm(total=btext_len, desc="start decrypt")
                        pbar_init = True

                    btext += str(pixels[y, x][2] % 2)
                    pbar.update(1)

            if decrypt_done:
                break

        if pbar:
            tqdm.close(pbar)

        # print(btext)
        sys.stdout.write(binary_to_string(btext))

    else:
        parser.error("Please specify either -e to encrypt or -d to decrypt.")
