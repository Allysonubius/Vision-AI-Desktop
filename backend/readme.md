# 🧠 Backend de Análise de Imagens (CNN + LLM)

Sistema de análise inteligente de superfícies de vias combinando **Visão Computacional (CNN)** e **Modelos de Linguagem (LLM)** em um pipeline híbrido.

---

## 🎯 Visão Geral

Este projeto implementa um backend capaz de:

* Classificar imagens em:

  * Asphalt
  * Cobblestone
  * Offroad
* Gerar análises descritivas com LLM
* Combinar visão computacional + interpretação semântica
* Armazenar histórico e métricas

👉 O foco não é apenas prever, mas **interpretar a imagem de forma contextual**.

---

## 🧠 Arquitetura

```text
Imagem → CNN → (baixa confiança?) → LLM → Resposta estruturada
```

### 🔥 Pipeline completo:

```text
[Frontend / Cliente]
        ↓
POST /vision/analyze
        ↓
image_service
        ↓
cnn_service (classificação)
        ↓
[Fallback se necessário]
        ↓
llm_service (análise multimodal)
        ↓
Parser + estruturação
        ↓
Resposta final (JSON)
```

---

## 🏗️ Estrutura do Projeto

```bash
backend/
│
├── api/               # Endpoints FastAPI
├── services/          # Lógica principal (core do sistema)
├── schemas/           # Validação (Pydantic)
├── database/          # SQLite e modelos
├── repositories/      # Acesso a dados
├── models/            # Modelos treinados (.pth)
├── uploads/           # Imagens recebidas
│
├── main.py            # Entrada da aplicação
└── app.db             # Banco local
```

---

## ⚙️ Tecnologias Utilizadas

| Categoria  | Stack                           |
| ---------- | ------------------------------- |
| Backend    | FastAPI, Python                 |
| IA (Visão) | PyTorch, TorchVision (ResNet18) |
| IA (Texto) | LLM via LM Studio               |
| Banco      | SQLite                          |
| Imagem     | PIL, OpenCV                     |

---

## 🚀 Funcionalidades

### 🔹 Classificação com CNN

* Modelo ResNet18 treinado
* Suporte a top-k predições
* Retorno estruturado com confiança

```json
{
  "label": "asphalt",
  "confidence": 0.87
}
```

---

### 🔹 Análise com LLM

* Geração de descrição da imagem
* Interpretação semântica
* Explicações do resultado da CNN

---

### 🔹 Pipeline híbrido (DIFERENCIAL)

* CNN executa primeiro
* LLM entra como fallback ou enriquecimento
* Balanceia performance + inteligência

---

### 🔹 Persistência

* Armazena análises no SQLite
* Cache de resultados
* Registro de métricas

---

## 🔌 API

### 📍 Análise de imagem

```bash
POST /vision/analyze
```

**Exemplo:**

```bash
curl -X POST http://localhost:8000/vision/analyze \
  -F "file=@imagem.jpg"
```

---

## 🧠 Camadas do Sistema

### 🔹 `image_service.py` (orquestrador)

Responsável por todo o fluxo:

* CNN → decisão → LLM → resposta final

---

### 🔹 `cnn_service.py`

* Carrega modelo `.pth`
* Executa inferência
* Retorna predição estruturada

---

### 🔹 `llm_service.py`

* Comunicação com LM Studio
* Suporte multimodal (texto + imagem)

---

### 🔹 `db_service.py`

* Persistência de análises
* Cache e métricas

---

## 🔧 Instalação

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração (.env)

```ini
MODEL_PATH=models/cnn_model_latest.pth

LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
MODEL_NAME=gpt-4

DB_PATH=app.db
```

---

## ▶️ Execução

```bash
uvicorn main:app --reload
```

---

## 🧠 Diferenciais Técnicos

* ✅ Pipeline híbrido (CNN + LLM)
* ✅ Fallback inteligente baseado em confiança
* ✅ Suporte multimodal
* ✅ Arquitetura modular (clean architecture)
* ✅ Preparado para evolução (MLOps / retraining)

---

## ⚠️ Limitações

* Dependência de modelo treinado
* LLM pode introduzir inconsistências
* Latência maior no fallback

---

## 🚀 Melhorias Futuras

* Ensemble de modelos
* Balanceamento automático de classes
* Monitoramento de métricas em tempo real
* Deploy com GPU
* Sistema de feedback para retraining

---

## 🧠 Resumo Técnico 

> Desenvolvi um backend modular com FastAPI que integra CNN para classificação de imagens e LLM multimodal para análise semântica, criando um pipeline híbrido capaz de interpretar imagens além da predição, com fallback inteligente e arquitetura escalável.