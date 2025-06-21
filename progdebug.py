from floppy import Parser as p

parser = p()
path = input("enter file name: ")

if path.endswith(".aap"):
    parser.parse_keys(path)
    print(f"parsed {path}")
else:
    parser.parse_keys(path + ".aap")
    print(f"parsed {path}.aap")