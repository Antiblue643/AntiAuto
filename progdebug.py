from floppy import Parser as p

parser = p()
path = input("enter file name: disk/")

if path.endswith(".aap") or path.endswith(".aaph"):
    parser.parse_keys(path)
    print(f"parsed {path}")
else:
    parser.parse_keys(path + ".aap")
    print(f"parsed {path}.aap")