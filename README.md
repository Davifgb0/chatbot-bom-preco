# 🛒 Assistente Virtual Inteligente — Rede de Supermercados "Bom Preço"

Projeto de portfólio desenvolvido durante o programa **AWS re/Start**, focado na resolução de um problema real do varejo utilizando conceitos de **Arquitetura em Nuvem (AWS)**, **IA Generativa (RAG)** e prototipagem funcional em **Python**.

---

## 🎯 O Problema e a Oportunidade
A Rede de Supermercados "Bom Preço" recebe centenas de mensagens diárias no WhatsApp com dúvidas repetitivas sobre ofertas da semana, horários de funcionamento e políticas de troca. O atendimento manual gera demora, perda de vendas e sobrecarga da equipe operacional.

**Solução:** Um Chatbot Inteligente conectado a uma base de conhecimento estruturada, capaz de responder em segundos com precisão, sugerir itens complementares (*cross-sell*) e transferir casos complexos para atendentes humanos.

---

## ☁️ Arquitetura Proposta na AWS

```text
[Cliente no WhatsApp] 
       │ (1. Envia pergunta em linguagem natural)
       ▼
[Amazon API Gateway] ──▶ [AWS Lambda (Python)]
                                │
                                ▼ (2. Consulta contexto + pergunta)
                       [Amazon Bedrock (RAG)] ◀── [Amazon S3 (Arquivos .txt)]
                                │
                                ▼ (3. Resposta fundamentada sem alucinações)
[Cliente no WhatsApp] ◀── [AWS Lambda / API Gateway]

'''

---

Amazon S3: Armazenamento centralizado dos arquivos da base de conhecimento (encarte_ofertas_semana.txt, info_lojas_horarios.txt, politica_trocas_faq.txt).

Amazon Bedrock (Knowledge Bases): Indexação semântica (RAG) para garantir respostas baseadas exclusivamente nos documentos da empresa.

AWS Lambda & API Gateway: Integração serverless em Python entre o canal de mensagens e o modelo de IA.

Amazon CloudWatch: Monitoramento de logs, latência e disponibilidade.

💻 Protótipo Funcional em Python
Para validar a lógica de ingestão de dados, busca por relevância e guardrails antes da implantação em escala na nuvem, foi desenvolvido um protótipo local em Python (chatbot_bom_preco.py) sem dependências externas.

Funcionalidades Implementadas:
Ingestão e Indexação: Leitura automática de múltiplos arquivos .txt estruturados por seções.

Normalização e Busca (Simulação de RAG): Remoção de acentos e stopwords para recuperar os trechos mais relevantes da base.

Regra de Cross-Sell: Sugestão automática de itens complementares (ex: carvão e bebidas) quando o cliente consulta carnes para churrasco.

Guardrail Anti-Alucinação: Bloqueio de respostas fora do escopo da base de conhecimento, encaminhando o cliente para atendimento humano.

🚀 Como Executar Localmente
Clone este repositório:

Bash
git clone https://github.com/Davifgb0/chatbot-bom-preco.git
cd chatbot-bom-preco
Execute o script em Python (requer Python 3.10+):

Bash
python chatbot_bom_preco.py
👨‍💻 Autor
Desenvolvido por Davi Francisco Gouvea Barcelos — Estudante de Cloud Computing (AWS re/Start) e Análise de Dados.
