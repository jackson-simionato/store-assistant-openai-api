def carrega(fname):
    try:
        with open(fname, 'r') as f:
            return f.read()
    except IOError:
        print(f"Error: File {fname} could not be read.")
        return None
    
def salva(fname):
    try:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write()
    except IOError:
        print(f"Error: File {fname} could not be written.")
        return None
    