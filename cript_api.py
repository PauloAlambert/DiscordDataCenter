import random
import re

ALFABETO = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def criptografar(texto, seed):
    rng = random.Random(seed)
    resultado = ""

    for char in texto:
        pos = ALFABETO.find(char)

        if pos != -1:
            shift = rng.randint(1, len(ALFABETO))
            novaPos = (pos + shift) % len(ALFABETO)
            charCriptografado = ALFABETO[novaPos]
            
            resultado += charCriptografado

            if re.match(r"[aeiouAEIOU]", charCriptografado):
                numeroAleatorio = str(rng.randint(0, 9))
                resultado += numeroAleatorio

            qtdLixo = rng.randint(0, 2)
            for _ in range(qtdLixo):
                lixoPos = rng.randint(0, len(ALFABETO) - 1)
                resultado += ALFABETO[lixoPos]
        else:
            resultado += char

    return resultado

def descriptografar(texto_criptografado, seed):
    rng = random.Random(seed)
    resultado = ""
    i = 0 

    while i < len(texto_criptografado):
        charCripto = texto_criptografado[i]
        pos = ALFABETO.find(charCripto)

        if pos != -1:
            shift = rng.randint(1, len(ALFABETO))
            novaPos = (pos - shift) % len(ALFABETO)
            resultado += ALFABETO[novaPos]
            
            i += 1 

            if re.match(r"[aeiouAEIOU]", charCripto):
                rng.randint(0, 9) 
                i += 1 

            qtdLixo = rng.randint(0, 2)
            for _ in range(qtdLixo):
                rng.randint(0, len(ALFABETO) - 1) 
                i += 1 
        else:
            resultado += charCripto
            i += 1

    return resultado