# 🧠 📦 Backend – Documentação Completa

## 🎯 Visão Geral

Este backend foi desenvolvido para suportar um sistema de análise de imagens de vias, combinando:

* **Visão computacional (CNN)**
* **Modelos de linguagem (LLM multimodal)**
* **API REST com FastAPI**
* **Pipeline inteligente com fallback**

O objetivo é permitir:

* Classificação de imagens (asphalt, cobblestone, offroad)
* Análise automática da imagem
* Interpretação crítica dos resultados

---

# 🏗️ Estrutura do Projeto

```bash
backend/
│
├── api/
├── services/
├── schemas/
├── database/
├── repositories/
├── models/
├── uploads/
├── main.py
└── app.db
```

---

# 🔹 1. Camada de API (`api/`)

Responsável por expor os endpoints HTTP.

## 📁 `api/routes/`

### ✔️ `vision.py`

* Endpoint principal de análise de imagem
* Recebe imagem (base64 ou file)
* Chama `image_service`

```python
POST /vision/analyze
```

👉 Função:

* Entrada do sistema de visão

---

### ✔️ `chat.py`

* Comunicação com LLM
* Permite interações adicionais

---

### ✔️ `history.py`

* Consulta histórico de análises

---

### ✔️ `health.py`

* Healthcheck do sistema

---

# 🔹 2. Camada de Services (`services/`)

👉 **Coração do sistema**

Aqui acontece toda a lógica.

---

## 🧠 `image_service.py` (ORQUESTRADOR)

Responsável por:

1. Receber imagem
2. Chamar CNN
3. Decidir fallback
4. Chamar LLM
5. Montar resposta final

### 🔥 Fluxo:

```text
Imagem → CNN → (falha?) → LLM → JSON final
```

---

## 🤖 `cnn_service.py`

Responsável por:

* Carregar modelo (`.pth`)
* Fazer inferência
* Retornar predição estruturada

### ✔️ Retorno padrão:

```json
{
  "label": "asphalt",
  "confidence": 0.87,
  "status": "success",
  "top_predictions": [...]
}
```

---

## 🧠 `llm_service.py`

Responsável por:

* Comunicação com LLM (LM Studio)
* Suporte a:

  * texto
  * imagem (base64)

### ✔️ Funções:

* `generate_response()` → texto
* `generate_response_with_image()` → multimodal

---

## 📊 `dataset_service.py` *(opcional)*

* Manipulação de datasets
* Pode ser usado para treino

---

## 🔁 `train_service.py` / `train_from_queue.py`

* Pipeline de treinamento
* Automatização de treino

👉 nível avançado (MLOps)

---

## 🔄 `retrain_queue.py`

* Fila de re-treinamento
* Permite evolução contínua do modelo

---

## 🧾 `session_service.py`

* Gerencia sessões de análise
* Armazena histórico

---

# 🔹 3. Schemas (`schemas/`)

Define estrutura de entrada/saída (Pydantic)

### ✔️ `image.py`

```python
class ImageRequest(BaseModel):
    image: str
```

---

### ✔️ `chat.py`

* Estrutura de mensagens

---

### ✔️ `history.py`

* Estrutura de histórico

---

# 🔹 4. Database (`database/`)

Gerencia persistência

---

### ✔️ `db.py`

* Conexão com banco (SQLite)

---

### ✔️ `models.py`

* Modelos ORM

---

### ✔️ `history.py`

* Histórico de interações

---

### ✔️ `result.py`

* Armazena resultados das análises

---

# 🔹 5. Repositories (`repositories/`)

Camada de acesso a dados

### ✔️ `image_repository.py`

* Persistência de imagens

---

👉 Serve para separar:

* lógica de negócio
* acesso ao banco

---

# 🔹 6. Models (`models/`)

Armazena modelos treinados:

```bash
cnn_model_latest.pth
```

---

# 🔹 7. Uploads (`uploads/`)

Armazena imagens enviadas

---

# 🔹 8. `main.py`

Ponto de entrada da aplicação

### Responsável por:

* Inicializar FastAPI
* Registrar rotas
* Subir servidor

---

# 🔥 Pipeline Completo (IMPORTANTE)

```text
[Cliente / Frontend]
        ↓
POST /vision/analyze
        ↓
image_service
        ↓
cnn_service
        ↓
[Se confiança baixa]
        ↓
llm_service (com imagem)
        ↓
Parser JSON
        ↓
Resposta estruturada
```

---

# 🧠 Diferenciais do Backend

## 🚀 1. Pipeline híbrido

* CNN + LLM
* fallback inteligente

---

## 🚀 2. Análise automática

* descrição da imagem
* análise crítica
* sugestões de melhoria

---

## 🚀 3. Arquitetura escalável

* separação por camadas
* fácil evolução

---

## 🚀 4. Suporte multimodal

* texto + imagem

---

# ⚠️ Limitações

* Dependência de modelo CNN treinado
* LLM não fornece probabilidade real
* Latência maior no fallback

---

# 🚀 Possíveis melhorias

* Ensemble CNN + LLM
* Métricas reais (precision/recall)
* Cache de inferência
* Deploy com GPU

---

# 🎯 Conclusão

Este backend implementa uma solução robusta para análise de imagens, indo além da simples classificação ao incorporar:

* interpretação semântica
* análise crítica automatizada
* arquitetura modular

---

# 🧠 Resumo (pra você usar em apresentação)

👉 “Construí um backend modular com FastAPI que combina CNN para classificação e LLM multimodal para análise crítica, criando um pipeline híbrido capaz de interpretar imagens além da predição.”

---
