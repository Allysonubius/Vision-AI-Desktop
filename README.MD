# 🧠 Vision AI Desktop — Electron + React + FastAPI + CNN + LLM

Aplicação desktop de **análise inteligente de imagens** com arquitetura híbrida:

* 🖥️ Frontend: Electron + React
* ⚙️ Backend: Python (FastAPI)
* 🧠 CNN: Classificação de superfícies (asphalt, cobblestone, offroad)
* 🤖 LLM Local: Interpretação técnica da imagem (ex: Gemma via LM Studio)
* 💾 Cache + Métricas: SQLite

---

# 🚀 Visão Geral

O sistema permite:

✔ Upload de imagem
✔ Classificação via CNN
✔ Análise técnica via LLM (context-aware)
✔ Correção inteligente da CNN (LLM override)
✔ Cache de resultados
✔ Métricas de performance
✔ Execução 100% local (sem dependência de cloud)

---

# 🏗️ Arquitetura

```
Electron (Desktop App)
   ↓
React (UI)
   ↓ HTTP
FastAPI (Backend)
   ├── CNN Service (classificação)
   ├── LLM Service (interpretação)
   ├── Image Service (orquestração)
   └── DB Service (cache + métricas)
```

---

# 📦 Tecnologias Utilizadas

## Frontend

* Electron
* React
* Zustand (estado)
* Fetch API

## Backend

* FastAPI
* Python 3.10+
* SQLite

## IA

* CNN custom (classificação de superfície)
* LLM local via LM Studio
* Modelo: Gemma (ex: gemma-4-e2b)

---

# 🧠 Fluxo de Processamento

1. Usuário envia imagem
2. Backend gera hash da imagem
3. Verifica cache (SQLite)
4. Se não existir:

   * CNN classifica imagem
   * LLM analisa contexto visual
5. Sistema valida resposta do LLM
6. Resultado final é salvo em cache
7. Métricas são registradas

---

# 🔍 Pipeline Detalhado

### 1. CNN

```json
{
  "label": "asphalt",
  "confidence": 0.87
}
```

---

### 2. LLM (interpretação)

O LLM recebe:

* contexto da imagem
* saída da CNN (não confiável)
* regras de decisão

E retorna:

```json
{
  "description": "...",
  "predicted_class_interpretation": "asphalt",
  "challenges": [],
  "critical_analysis": "...",
  "limitations": "...",
  "improvements": []
}
```

---

### 3. Validação

* JSON parsing seguro
* validação de campos obrigatórios
* fallback em caso de erro

---

### 4. Cache

* baseado em hash da imagem
* evita reprocessamento
* ignora respostas inválidas

---

# 🖥️ Frontend (Electron + React)

## Estrutura

```
/src
  /components
  /pages
  /store
  /services
```

## Estado global

Gerenciado com Zustand:

```js
const useChatStore = create((set) => ({
  sessions: [],
  activeSession: null
}));
```

## Comunicação com backend

```js
fetch("http://127.0.0.1:8000/vision/analyze", {
  method: "POST",
  body: JSON.stringify({ image })
});
```

---

# ⚙️ Backend (FastAPI)

## Rotas principais

### POST `/vision/analyze`

Entrada:

```json
{
  "image": "base64"
}
```

Saída:

```json
{
  "prediction": "asphalt",
  "confidence": 0.87,
  "analysis": {...},
  "metrics": {...}
}
```

---

# 🧩 Estrutura Backend

```
/services
  cnn_service.py
  llm_service.py
  image_service.py
  db_service.py

/core
  config.py

/routes
  vision.py
```

---

# 🗄️ Banco de Dados

SQLite com duas tabelas:

## image_analysis

| campo      | descrição    |
| ---------- | ------------ |
| image_hash | hash único   |
| prediction | classe final |
| confidence | confiança    |
| analysis   | JSON do LLM  |
| status     | processed    |

---

## metrics

| campo       | descrição     |
| ----------- | ------------- |
| cnn_latency | tempo CNN     |
| llm_latency | tempo LLM     |
| llm_tokens  | uso de tokens |

---

# 🧪 Execução do Projeto

## 1. Backend

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 2. LLM Local

1. Instale LM Studio
2. Baixe modelo (ex: Gemma)
3. Inicie servidor local (porta padrão)

---

## 3. Frontend

```bash
npm install
npm run electron
```

---

# ⚠️ Problemas Comuns

## ❌ JSON inválido do LLM

Solução:

* parser robusto
* retry automático

---

## ❌ Cache retornando erro

Solução:

```sql
DELETE FROM image_analysis;
```

---

## ❌ CORS no Electron

Solução no FastAPI:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)
```

---

## ❌ LLM retornando texto ao invés de JSON

Solução:

* prompt restritivo
* validação + fallback

---

# 🔒 Boas Práticas Implementadas

✔ Validação de resposta do LLM
✔ Retry automático
✔ Cache inteligente
✔ Normalização de classes
✔ Separação de responsabilidades
✔ Logs estruturados

---

# 🚀 Próximos Passos

* 🔍 Highlight visual da imagem (features detectadas)
* 📊 Dashboard de métricas
* 🧠 Fine-tuning do modelo CNN
* 🔄 Streaming de resposta do LLM
* 💬 Interface estilo chat com histórico

---

# 🧠 Conceitos Importantes

* CNN ≠ verdade absoluta
* LLM atua como interpretador semântico
* Sistema híbrido melhora precisão
* Cache é essencial para performance

---

# 📌 Licença

Uso educacional e experimental.

---

# 👨‍💻 Autor

Projeto focado em arquitetura de sistemas inteligentes locais com integração entre visão computacional e modelos de linguagem.

---
