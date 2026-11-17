"""Classe Assistente: atendimento, histórico, indicadores e exportação CSV."""
import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import nivel_confianca

AVISO_DADOS = "Atenção: não digite CPF, telefone ou e-mail. Reescreva."
CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_s", "nota"]


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        pasta = os.path.dirname(base.caminho) or "."
        self.caminho_historico = os.path.join(pasta, "historico.json")
        self.caminho_csv = os.path.join(pasta, "atendimentos.csv")
        self.historico = []
        self.inicio_sessao = 0
        self.carregar_historico()

    # ---------- entrada segura ----------
    def _entrada(self, mensagem):
        try:
            return input(mensagem)
        except EOFError:
            return "0"

    def _escolher(self, maximo):
        """Pede um número de 0 a maximo; repete até ser válido."""
        while True:
            texto = self._entrada("Escolha uma opção: ").strip()
            if texto.isdigit() and 0 <= int(texto) <= maximo:
                return int(texto)
            print(f"Opção inválida. Digite um número de 0 a {maximo}.")

    def _pedir_sn(self, mensagem):
        while True:
            texto = self._entrada(mensagem).strip().lower()
            if texto in ("s", "sim"):
                return True
            if texto in ("n", "nao", "não"):
                return False
            print("Resposta inválida. Digite s ou n.")

    @staticmethod
    def tem_dado_pessoal(texto):
        digitos = sum(1 for c in texto if c.isdigit())
        return digitos >= 8 or "@" in texto

    # ---------- histórico ----------
    def carregar_historico(self):
        self.historico = []
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if isinstance(dados, list):
                self.historico = [d for d in dados if isinstance(d, dict)]
            else:
                raise ValueError("formato inesperado")
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError, OSError):
            print("Aviso: historico.json corrompido; começando um histórico novo.")
            try:
                os.replace(self.caminho_historico, self.caminho_historico + ".bak")
            except OSError:
                pass
        self.inicio_sessao = len(self.historico)

    def salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        self.historico.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_s": tempo,
            "nota": None,
        })
        self.salvar_historico()

    # ---------- atendimento por texto livre ----------
    def perguntar(self):
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível no momento.")
            return
        inicio = time.time()
        tentativas = 0
        encontrou = False
        ajudou = False
        ultima_pergunta = ""
        ultimo_id = None

        while True:
            texto = self._entrada("\nDigite sua dúvida (0 para voltar): ").strip()
            if texto == "0":
                break
            if not texto:
                print("Você não digitou nada. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if self.tem_dado_pessoal(texto):
                print(AVISO_DADOS)   # recusada e NÃO registrada
                continue

            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)

            if not resultados or resultados[0][0] < 3:
                encontrou, ultimo_id = False, None
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (ex.: o nome do documento ou do serviço) "
                      "ou use a navegação por categorias.")
                print("Categorias: " + ", ".join(self.base.categorias()))
                continue

            pontos, melhor = resultados[0]
            encontrou, ultimo_id = True, melhor.id
            print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()

            alternativas = [(p, o) for p, o in resultados[1:3] if p >= 3]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for p, o in alternativas:
                    print(f"  - {o.titulo} ({p} pontos)")

            ajudou = self._pedir_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
            if ajudou:
                break
            print("Tudo bem. Tente reescrever sua dúvida com outras palavras.")

        if tentativas > 0:
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", ultima_pergunta, ultimo_id, encontrou, ajudou, tentativas, tempo)

    # ---------- navegação por categorias ----------
    def navegar(self):
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível no momento.")
            return
        while True:
            categorias = self.base.categorias()
            print("\n=== Categorias ===")
            for i, cat in enumerate(categorias, start=1):
                print(f"{i}. {cat}")
            print("0. Voltar")
            escolha = self._escolher(len(categorias))
            if escolha == 0:
                return
            categoria = categorias[escolha - 1]

            while True:
                itens = self.base.por_categoria(categoria)
                print(f"\n=== {categoria} ===")
                for i, o in enumerate(itens, start=1):
                    print(f"{i}. {o.titulo}")
                print("0. Voltar")
                escolha = self._escolher(len(itens))
                if escolha == 0:
                    break
                inicio = time.time()
                orientacao = itens[escolha - 1]
                orientacao.exibir()
                ajudou = self._pedir_sn("\nEssa orientação respondeu sua dúvida? (s/n): ")
                tempo = round(time.time() - inicio, 1)
                self.registrar("categoria", orientacao.titulo, orientacao.id, True, ajudou, 1, tempo)

    # ---------- indicadores ----------
    def indicadores(self):
        total = len(self.historico)
        print("\n=== Indicadores ===")
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return
        encontrados = [h for h in self.historico if h.get("encontrou")]
        ajudaram = [h for h in self.historico if h.get("ajudou")]
        tempos = [h["tempo_s"] for h in encontrados if isinstance(h.get("tempo_s"), (int, float))]
        tentativas = [h["tentativas"] for h in self.historico if isinstance(h.get("tentativas"), int)]
        notas = [h["nota"] for h in self.historico if isinstance(h.get("nota"), int)]

        print(f"Atendimentos registrados:    {total}")
        print(f"Resposta encontrada (%):     {len(encontrados) / total * 100:.1f}")
        print(f"Taxa de acerto: ajudou (%):  {len(ajudaram) / total * 100:.1f}")
        if tempos:
            print(f"Tempo médio para encontrar:  {sum(tempos) / len(tempos):.1f} s")
        else:
            print("Tempo médio para encontrar:  sem dados")
        if tentativas:
            print(f"Tentativas por atendimento:  {sum(tentativas) / len(tentativas):.1f}")
        if notas:
            print(f"Facilidade de uso (1 a 5):   {sum(notas) / len(notas):.1f}")
        else:
            print("Facilidade de uso (1 a 5):   sem notas")

        sem_solucao = []
        for h in self.historico:
            if not h.get("ajudou") and h.get("pergunta") and h["pergunta"] not in sem_solucao:
                sem_solucao.append(h["pergunta"])
        print("Dúvidas sem solução:")
        if sem_solucao:
            for p in sem_solucao:
                print(f"  - {p}")
        else:
            print("  (nenhuma)")

    # ---------- CSV ----------
    def exportar_csv(self):
        if not self.historico:
            print("Não há atendimentos para exportar.")
            return
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as f:
                escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV, delimiter=";")
                escritor.writeheader()
                for h in self.historico:
                    escritor.writerow({campo: h.get(campo, "") for campo in CAMPOS_CSV})
            print(f"{len(self.historico)} atendimentos exportados para {self.caminho_csv}")
        except OSError:
            print("Aviso: não foi possível gravar o CSV (feche o arquivo se ele estiver aberto).")

    # ---------- saída ----------
    def pedir_nota(self):
        """Ao sair, pede nota de facilidade (1 a 5) e grava nos atendimentos desta sessão."""
        if len(self.historico) <= self.inicio_sessao:
            return
        while True:
            texto = self._entrada("De 1 a 5, qual a facilidade de usar o assistente? (0 para pular): ").strip()
            if texto.isdigit() and 0 <= int(texto) <= 5:
                break
            print("Nota inválida. Digite um número de 1 a 5 (ou 0 para pular).")
        if int(texto) == 0:
            return
        for h in self.historico[self.inicio_sessao:]:
            h["nota"] = int(texto)
        self.salvar_historico()
        print("Obrigado pela avaliação!")

    def menu(self):
        print(f"\n===== {self.nome} =====")
        print("Orientações com fonte e data de verificação. Não pedimos dados pessoais.")
        print("Aviso: este assistente NÃO é um canal oficial.")
        while True:
            print("\n--- Menu ---")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos para CSV")
            print("0. Sair")
            opcao = self._escolher(4)
            if opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self.pedir_nota()
                print("Até logo!")
                return
