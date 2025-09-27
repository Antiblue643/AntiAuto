from floppy import Parser as p

parser = p()
path = input("enter file name: disk/")

if path.endswith(".aap") or path.endswith(".aaph"):
    parser.parse_keys(path)
    print(f"parsed {path}")
else:
    try:
        parser.parse_keys(path + ".aaph")
        print(f"parsed {path}.aaph")
    except FileNotFoundError:
        try:
            parser.parse_keys(path + ".aap")
            print(f"parsed {path}.aap")
        except FileNotFoundError:
            print("file not found, exiting")
            exit()