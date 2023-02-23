#import
from pathlib import Path
import struct
import argparse
import datetime
import shutil


def print_one_value(file, lastGroup=False):
    leng = file.read(1)
    if leng == b'':
        return False
    group = file.read(int.from_bytes(leng, byteorder="little"))
    typ = int.from_bytes(file.read(2), byteorder="little")
    if typ == 5:  # container elements
        val = file.read(5)
        if lastGroup:
            print()
            print("####################")
        print(group.decode('ascii'), end="\t")
        typ = print_one_value(file, True)
    elif typ == 2:  # float64
        val = file.read(8)
        print(struct.unpack('d', val)[0])
        file.read(1)
    elif typ == 1:  # bool
        val = int.from_bytes(file.read(2), byteorder="little")
        if val == 1:
            print("True")
        else:
            print("False")
    elif typ == 3:  # text
        file.read(1)
        lenStr = file.read(1)
        group = file.read(int.from_bytes(lenStr, byteorder="little"))
        print("'" + group.decode("ascii") + "'")
        file.read(1)
    else:
        print("typ"), print(typ), print("Nicht bekannt")
    return typ


parser = argparse.ArgumentParser(
    description="This tool reads or writes factorio mod settings. Read the settings if no parameters are given.",
    epilog="Remember to Backup your mod-settings.dat before usage!")
parser.add_argument("-s", "--setting", nargs='?', help="Name of the setting to be edited. Prints also the current value if found.")
parser.add_argument("-v", "--value", nargs='?', help="The value to be set needs to be compatible with the current value.")
parser.add_argument("-p", "--path", help="path to mod-setings.dat")

# read arguments from the command line
args = parser.parse_args()


if hasattr(args, 'setting') and args.setting is not None:  # returns False:
    date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = Path(args.path+"."+date)
    if not backup_file.is_file():
        shutil.copy2(args.path, args.path+"."+date)
    with open(args.path, mode="r+b") as file:
        data = file.read()
        position = data.find(args.setting.encode("ascii"))
        if position > 0:
            file.seek(0)
            before = file.read(position-1)
            typ = print_one_value(file)
            after = file.read()
            if hasattr(args, 'value') and args.value is not None:
                before += int.to_bytes(len(args.setting.encode("ascii")), 1, "little")
                before += args.setting.encode("ascii")
                before += b'\x05\x00\x01\x00\x00\x00\x00'
                before += b'\x05value'
                before += int.to_bytes(typ, 2, "little")
                if typ == 1:
                    if args.value in ['true', 'True', 'TRUE', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
                        before += int.to_bytes(1, 1, "little")
                    elif args.value in ['false', 'False', 'FALSE', '0', 'f', 'n', 'no', 'nope', 'nej', 'certainly not', 'eh-eh']:
                        before += int.to_bytes(0, 1, "little")
                    else:
                        print("come on! Be a little more decisive, cant interpret your input as BOOLEAN, and i am really trying hard!")
                        exit(1)
                elif typ == 2:
                    val = float(args.value)
                    before += bytearray(struct.pack("d", val))

                elif typ == 3:
                    before += b'\x00'
                    before += int.to_bytes(len(args.value.encode("ascii")), 1, "little")
                    before += args.value.encode("ascii")
                if len(after) > 0:
                    before += b'\x00' + after
                file.truncate(0)
                file.seek(0)
                file.write(before)
                pos = before.find(args.setting.encode("ascii"))
                file.seek(pos-1)
                print("After writing:")
                typ = print_one_value(file)
        else:
            print(args.setting + " not found!")
else:
    with open(args.path, mode="rb") as file:
        file.seek(0x10)
        while print_one_value(file):
            True
