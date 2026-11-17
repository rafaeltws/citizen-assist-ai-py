"""Classe BaseConhecimento: lê o JSON, lista categorias e busca por pontuação."""
import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
MINIMO_PALAVRA_TITULO = 4
LIMITE_ALTA = 6
LIMITE_MEDIA = 3


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação; espaço nas pontas para casar palavra inteira."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def nivel_confianca(pontos):
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava: devolve True/False."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Aviso: arquivo {self.caminho} não encontrado.")
            return False
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            print(f"Aviso: arquivo {self.caminho} está corrompido ou ilegível.")
            return False

        if not isinstance(dados, list):
            print("Aviso: a base de conhecimento deve ser uma lista de orientações.")
            return False

        for posicao, registro in enumerate(dados, start=1):
            try:
                self.orientacoes.append(Orientacao.de_dicionario(registro))
            except (ValueError, TypeError) as erro:
                print(f"Aviso: registro {posicao} ignorado ({erro}).")
        return len(self.orientacoes) > 0

    def categorias(self):
        """Lista de categorias, sem repetir, na ordem em que aparecem."""
        vistas = []
        for o in self.orientacoes:
            if o.categoria not in vistas:
                vistas.append(o.categoria)
        return vistas

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, orientacao, pergunta):
        """+3 por palavra-chave que aparece na pergunta; +1 por palavra (4+ letras)
        da pergunta que aparece no título."""
        pergunta_norm = normalizar(pergunta)
        pontos = 0
        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE
        titulo_norm = normalizar(orientacao.titulo)
        for palavra in set(pergunta_norm.split()):
            if len(palavra) >= MINIMO_PALAVRA_TITULO and f" {palavra} " in titulo_norm:
                pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor pontuação."""
        resultados = []
        for o in self.orientacoes:
            pontos = self.pontuar(o, pergunta)
            if pontos > 0:
                resultados.append((pontos, o))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
