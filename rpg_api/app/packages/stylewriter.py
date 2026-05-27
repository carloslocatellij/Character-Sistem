

from pyfiglet import figlet_format

import time
import sys

def typing_print(text, speed=0.003):
    """Simula o efeito de digitação, imprimindo o texto caracter por caracter."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


texto_estilizado = figlet_format("CharSistem RPG", font="slant_relief")


# for line in texto_estilizado:
#     typing_print(line)
typing_print(texto_estilizado)