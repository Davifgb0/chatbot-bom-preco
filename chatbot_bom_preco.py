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
    "custa", "aceitam", "abre", "funciona", "faco", "quero", "saber", "sobre"
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

        # Divide por linhas não vazias mantendo contexto de seção
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


def buscar_resposta(pergunta: str, base: list[dict]) -> str:
    """Busca os trechos mais relevantes na base (simulando RAG) e monta a resposta."""
    # Normaliza variações comuns de verbos para substantivos da base
    pergunta_ajustada = normalizar_texto(pergunta).replace("trocar", "troca").replace("defeito", "avariado")
    palavras_pergunta = extrair_palavras_chave(pergunta_ajustada)

    if not palavras_pergunta:
        return (
            "Não consegui identificar o que você procura. "
            "Você pode perguntar sobre ofertas da semana, horários das lojas, "
            "formas de pagamento ou política de trocas!"
        )

    resultados = []
    for item in base:
        intersecao = palavras_pergunta.intersection(item["palavras"])
        if intersecao:
            resultados.append((len(intersecao), item))

    resultados.sort(key=lambda x: x[0], reverse=True)

    if not resultados:
        return (
            "Desculpe, não encontrei essa informação nos nossos registros atuais.\n"
            "Gostaria que eu transferisse seu atendimento para um atendente humano da loja?"
        )

    # Evita exibir linhas duplicadas no resultado final
    top_trechos = []
    textos_vistos = set()
    for score, item in resultados:
        if item["texto"] not in textos_vistos:
            top_trechos.append(item)
            textos_vistos.add(item["texto"])
        if len(top_trechos) == 4:
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
    print("=" * 60)
    print("  ASSISTENTE VIRTUAL - REDE DE SUPERMERCADOS BOM PREÇO")
    print("  Digite sua dúvida ou 'sair' para encerrar o atendimento.")
    print("=" * 60)

    base = carregar_base_conhecimento(ARQUIVOS_BASE)
    if not base:
        print("Erro: Nenhum arquivo da base de conhecimento foi carregado.")
        return

    print(f"Base carregada com sucesso ({len(base)} registros indexados).\n")

    while True:
        pergunta = input("Você: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "encerrar"}:
            print("\nBot Bom Preço: Obrigado pelo contato! Boas compras!")
            break

        resposta = buscar_resposta(pergunta, base)
        print(f"\nBot Bom Preço:\n{resposta}\n")
        print("-" * 60)


if __name__ == "__main__":
    iniciar_chat()