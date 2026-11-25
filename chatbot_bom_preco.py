import os
import re
import unicodedata

# Lista dos arquivos que formam a Base de Conhecimento
ARQUIVOS_BASE = [
    "encarte_ofertas_semana.txt",
    "info_lojas_horarios.txt",
    "politica_trocas_faq.txt",
]

# Palavras comuns ignoradas na hora de buscar relevância
STOPWORDS = {
    "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "e", "ou",
    "que", "qual", "quais", "como", "onde", "quando", "tem", "voces", "voce",
    "hoje", "esta", "estao", "sao", "ser", "ter", "valor", "preco", "quanto",
    "custa", "aceitam", "abre", "funciona", "faco", "quero", "saber", "sobre",
    "dia", "semana", "tudo", "todos", "todas", "lista", "ver", "mostrar"
}

# Termos que indicam que o cliente quer ver o encarte completo de promoções
GATILHOS_ENCARTE_COMPLETO = {
    "promocao", "promocoes", "oferta", "ofertas", "encarte",
    "desconto", "descontos", "barato", "baratos", "catalogo"
}


def normalizar_texto(texto: str) -> str:
    """Remove acentos e deixa tudo em minúsculo para facilitar a busca."""
    texto_nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto_nfkd if not unicodedata.combining(c))


def extrair_palavras_chave(texto: str) -> set[str]:
    """Extrai termos relevantes da pergunta do usuário."""
    limpo = re.sub(r"[^a-z0-9\s]", " ", normalizar_texto(texto))
    return {p for p in limpo.split() if len(p) > 2 and p not in STOPWORDS}


def carregar_base_conhecimento(arquivos: list[str]) -> list[dict]:
    """Lê os arquivos .txt e separa o conteúdo em blocos pesquisáveis."""
    blocos = []
    for nome_arquivo in arquivos:
        if not os.path.exists(nome_arquivo):
            print(f"[AVISO] Arquivo não encontrado na pasta: {nome_arquivo}")
            continue

        with open(nome_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()

        secao_atual = "Geral"
        for linha in conteudo.splitlines():
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa.startswith("="):
                continue

            if linha_limpa.startswith("[") and linha_limpa.endswith("]"):
                secao_atual = linha_limpa
                continue

            blocos.append({
                "fonte": nome_arquivo,
                "secao": secao_atual,
                "texto": linha_limpa,
                "palavras": extrair_palavras_chave(f"{secao_atual} {linha_limpa}")
            })
    return blocos


def listar_todas_ofertas(base: list[dict]) -> str:
    """Retorna todas as ofertas cadastradas no encarte organizadas por seção."""
    itens_encarte = [b for b in base if b["fonte"] == "encarte_ofertas_semana.txt"]

    if not itens_encarte:
        return "No momento não encontrei ofertas cadastradas no encarte da semana."

    linhas = ["Confira todas as ofertas disponíveis hoje na Rede Bom Preço:\n"]
    secao_anterior = None

    for item in itens_encarte:
        if item["secao"] != secao_anterior:
            linhas.append(f"\n  {item['secao']}")
            secao_anterior = item["secao"]
        linhas.append(f"    • {item['texto']}")

    linhas.append("\n[Fonte consultada: encarte_ofertas_semana.txt]")
    return "\n".join(linhas)


def exibir_sugestoes():
    """Mostra exemplos de perguntas que o usuário pode fazer ao bot."""
    print("💡 Exemplos do que você pode perguntar:")
    print("  1. O que vocês têm em promoção hoje?")
    print("  2. Qual o horário de funcionamento e endereço das lojas?")
    print("  3. Quais formas de pagamento vocês aceitam? (Pix, VR/VA?)")
    print("  4. Como funciona a política de troca de produtos?")
    print("  5. Vocês fazem entrega / delivery?")
    print("  (Digite 'ajuda' para ver esta lista novamente ou 'sair' para encerrar)\n")


def buscar_resposta(pergunta: str, base: list[dict]) -> str:
    """Busca os trechos mais relevantes na base (simulando RAG) e monta a resposta."""
    pergunta_ajustada = (
        normalizar_texto(pergunta)
        .replace("trocar", "troca")
        .replace("defeito", "avariado")
    )
    palavras_pergunta = extrair_palavras_chave(pergunta_ajustada)

    if not palavras_pergunta:
        return (
            "Não consegui identificar o que você procura. "
            "Digite 'ajuda' para ver exemplos de perguntas!"
        )

    # Se o usuário perguntou de forma geral sobre promoções/ofertas, mostra o encarte inteiro
    if palavras_pergunta.issubset(GATILHOS_ENCARTE_COMPLETO) or (
        palavras_pergunta.intersection(GATILHOS_ENCARTE_COMPLETO) and len(palavras_pergunta) <= 2
    ):
        return listar_todas_ofertas(base)

    resultados = []
    for item in base:
        intersecao = palavras_pergunta.intersection(item["palavras"])
        if intersecao:
            resultados.append((len(intersecao), item))

    resultados.sort(key=lambda x: x[0], reverse=True)

    if not resultados:
        return (
            "Desculpe, não encontrei essa informação nos nossos registros atuais.\n"
            "Digite 'ajuda' para ver o que eu consigo responder ou peça para falar com um atendente."
        )

    top_trechos = []
    textos_vistos = set()
    for score, item in resultados:
        if item["texto"] not in textos_vistos:
            top_trechos.append(item)
            textos_vistos.add(item["texto"])
        if len(top_trechos) == 6:
            break

    linhas_resposta = ["Aqui está o que encontrei para você na Rede Bom Preço:\n"]
    for item in top_trechos:
        linhas_resposta.append(f"  • {item['texto']}")

    termos_churrasco = {"picanha", "carne", "alcatra", "frango", "linguica", "churrasco"}
    if palavras_pergunta.intersection(termos_churrasco):
        linhas_resposta.append(
            "\nDica do Bom Preço: Vai fazer churrasco? Aproveite também o "
            "Carvão Vegetal 3kg e nossas bebidas em oferta no encarte da semana!"
        )

    fontes_usadas = sorted({item["fonte"] for item in top_trechos})
    linhas_resposta.append(f"\n[Fonte consultada: {', '.join(fontes_usadas)}]")

    return "\n".join(linhas_resposta)


def iniciar_chat():
    print("=" * 64)
    print("  ASSISTENTE VIRTUAL - REDE DE SUPERMERCADOS BOM PREÇO")
    print("=" * 64)

    base = carregar_base_conhecimento(ARQUIVOS_BASE)
    if not base:
        print("Erro: Nenhum arquivo da base de conhecimento foi carregado.")
        return

    print(f"Base carregada com sucesso ({len(base)} registros indexados).\n")
    exibir_sugestoes()

    while True:
        pergunta = input("Você: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "encerrar"}:
            print("\nBot Bom Preço: Obrigado pelo contato! Boas compras!")
            break
        if pergunta.lower() in {"ajuda", "menu", "opcoes", "opções"}:
            print()
            exibir_sugestoes()
            continue

        resposta = buscar_resposta(pergunta, base)
        print(f"\nBot Bom Preço:\n{resposta}\n")
        print("-" * 64)


if __name__ == "__main__":
    iniciar_chat()