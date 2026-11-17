"""Classe Orientacao: representa um registro da base de conhecimento."""


class Orientacao:
    CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
              "documentos", "onde", "fonte", "verificado_em"]

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Cria uma Orientacao a partir de um dicionário do JSON.
        Lança ValueError se faltar campo ou se o tipo estiver errado."""
        if not isinstance(dados, dict):
            raise ValueError("registro não é um dicionário")
        faltando = [c for c in cls.CAMPOS if c not in dados]
        if faltando:
            raise ValueError("campos ausentes: " + ", ".join(faltando))
        if not isinstance(dados["palavras_chave"], list) or not isinstance(dados["documentos"], list):
            raise ValueError("palavras_chave e documentos devem ser listas")
        return cls(**{campo: dados[campo] for campo in cls.CAMPOS})

    def exibir(self):
        print(f"\n>> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for doc in self.documentos:
                print(f"  - {doc}")
        else:
            print("Documentos necessários: nenhum")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
