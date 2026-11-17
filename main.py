"""Citizen Assist AI - assistente de orientação ao cidadão (terminal)."""
import os

from assistente import Assistente
from base_conhecimento import BaseConhecimento

PASTA = os.path.dirname(os.path.abspath(__file__))


def main():
    base = BaseConhecimento(os.path.join(PASTA, "data", "base_conhecimento.json"))
    base.carregar()          # lê o JSON e cria os objetos Orientacao
    assistente = Assistente("Citizen Assist AI", base)
    assistente.menu()


if __name__ == "__main__":
    main()
