#import
import struct
print("halo welt")
with open("mod-settings.dat", mode="rb") as file:  # Use file to refer to the file object
    file.seek(0x10)
    while True:
        leng = file.read(1)
        if leng == b'':
            break
        group = file.read(int.from_bytes(leng, byteorder="little"))
        typ = int.from_bytes(file.read(2), byteorder="little")
        if typ == 5:  # container elements
            val = file.read(5)
            print(group.decode('ascii'), end=" ")
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
            print("'"+group.decode("ascii")+"'")
            file.read(1)
        else:
            print("typ"),print(typ),print("Nicht bekannt")


