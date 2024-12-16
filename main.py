# project imports
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image
import threading
import codecs
import os
import sys
import time

# output colors and formatting values
YELLOW = "\033[93m"
GREEN = "\033[94m"
RED = "\033[91m"
WHITE = "\033[97m"
KEY_WIDTH = 30
VALUE_WIDTH = 10
ERROR_BYTES_MSG = RED + "Unable to decode bytes"
ERROR_MSG = RED + "Error occurred"
ERROR_PATH_MSG = "[-] UNABLE TO LOCATE DIRECTORY !! \n"
CREATION_MSG = "Creation Time: {{:>{}}}".format(39)
RESULT_FORMAT = "{{:<{}}}{{:<{}}}".format(KEY_WIDTH, VALUE_WIDTH)


def data_formatter(value):
    """
    This function takes in a dictionary value and formats it. Currently processes bytes and dictionaries.
    If the value is of type dict then it traverses it recusively.
    """
    if isinstance(value, bytes):
        try:
            # try to decode the byted value using the codecs module
            formatted_value = codecs.decode(value, errors="backslashreplace")
        except ValueError as byteerror:
            # if the data can't be decoded, return an error
            formatted_value = ERROR_BYTES_MSG
        except Exception as error:
            formatted_value = ERROR_MSG
    elif isinstance(value, dict):
        for mini_key, mini_val in value.items():
            t = GPSTAGS.get(mini_key, mini_key)
            res = data_formatter(mini_val)
            formatted_value = f"{t} : {res}"
    else:
        formatted_value = GREEN + str(value)

    return formatted_value


def extract_image_data(target_dir: str):
    """
    This function checks if the provided value is a directory.
    If it is, it returns available information for images in the directory.
    """
    if os.path.isdir(target_dir):
        try:
            target_images = [os.path.join(target_dir, file) for file in os.listdir(
                target_dir) if file.endswith(".jpg") or file.endswith(".png")]

            for img in target_images:
                # Return the metadata change time of a file, reported by os.stat().
                # On some systems (like Unix) is the time of the last metadata change, and, on others (like Windows), is the creation time
                created_time = os.path.getctime(img)
                created_time = time.ctime(created_time)

                # read the image file
                read_file = Image.open(img)

                exif_data = read_file._getexif() if read_file._getexif() != None else {}

                # # if the image contains any info
                # split the img name based on specific os filesystem separator ie \\ on window and / on unix and mac
                sys.stdout.write(YELLOW + f"\n=============== EXIF info for {img.split(os.path.sep)[-1]} =================== \n" + GREEN)
                sys.stdout.write(
                    GREEN + CREATION_MSG.format(created_time) + "\n" + WHITE)
                if exif_data:
                    for key, value in exif_data.items():
                        # get the value of the number key from TAGS
                        exif_data_key = TAGS.get(key, key)

                        # get the value at the key and format it
                        result_value = data_formatter(value)

                        sys.stdout.write(
                            GREEN + RESULT_FORMAT.format(exif_data_key, result_value) + "\n" + WHITE)
                else:
                    # if an image has no exif data recorded
                    sys.stdout.write(RED + "[-] Data unavailable \n" + WHITE)
        except Exception as err:
            sys.stdout.write(
                RED + "[-] " + ERROR_MSG + str(err) + "\n" + WHITE)
            sys.exit(1)
    else:
        # exit program with exit code 1 if target directory is not valid
        sys.stdout.write(RED + ERROR_PATH_MSG + WHITE)
        sys.exit(1)


if __name__ == "__main__":
    target_dir = input("$ Enter Path to image(s) folder: ").strip()
    tar = threading.Thread(target=extract_image_data, args=(target_dir,))
    tar.start()