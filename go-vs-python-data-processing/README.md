# Go vs Python - Data Processing Performance Comparison

## 🎯 Objetivo

Comparar desempenho entre **Go** e **Python** no processamento e paralelismo com dados, analisando diferentes cenários de uso e identificando as melhores práticas para cada linguagem.

## 🛠️ Tecnologias Usadas

### Go
- **Goroutines** - Concorrência nativa do Go
- **sync.WaitGroup** - Sincronização de goroutines
- **time** - Medição de tempo de execução
- **pprof** - Profiling de performance
- **runtime** - Informações de runtime

### Python
- **Pandas** - Manipulação de dados
- **multiprocessing** - Paralelismo real
- **threading** - Concorrência com threads
- **concurrent.futures** - API de alto nível para execução assíncrona
- **psutil** - Monitoramento de recursos do sistema

## 🚀 Como Executar os Testes

### Pré-requisitos

**Go:**
```bash
# Instalar dependências
go mod tidy
```

**Python:**
```bash
# Instalar dependências
pip install -r requirements.txt
```

### Executando os Benchmarks

**Go:**
```bash
# Executar processamento de dados
go run go/process_data.go

# Executar testes com goroutines
go run go/goroutines.go

# Executar benchmarks
cd go/benchmarks
go test -bench=. -benchmem
```

**Python:**
```bash
# Executar processamento de dados
python python/process_data.py

# Executar testes com threads paralelas
python python/parallel_threads.py

# Executar benchmarks
cd python/benchmarks
python -m pytest --benchmark-only
```

## 📊 Como Medir Performance

### Ferramentas de Medição

**Go:**
- `time` - Tempo de execução
- `pprof` - CPU e memory profiling 
- `runtime.MemStats` - Estatísticas de memória
- `go test -bench` - Benchmarks automáticos

**Python:**
- `time` - Tempo de execução
- `psutil` - CPU, memória e I/O
- `cProfile` - Profiling detalhado
- `memory_profiler` - Monitoramento de memória
- `pytest-benchmark` - Benchmarks automáticos

### Comandos de Profiling

**Go:**
```bash
# CPU profiling
go run -cpuprofile=cpu.prof go/process_data.go
go tool pprof cpu.prof

# Memory profiling
go run -memprofile=mem.prof go/process_data.go
go tool pprof mem.prof
```

**Python:**
```bash
# CPU profiling
python -m cProfile -o profile.prof python/process_data.py

# Memory profiling
python -m memory_profiler python/process_data.py
```

## 📈 Resultados

### Comparação de Tempo de Execução

| Cenário | Go | Python | Diferença |
|---------|----|---------|---------:|
| Leitura CSV (1MB) | - | - | - |
| Processamento sequencial | - | - | - |
| Processamento paralelo | - | - | - |
| Cálculos agregados | - | - | - |

> **Nota:** Os resultados detalhados estão disponíveis em [`results/time_comparison.md`](results/time_comparison.md)

### Uso de Recursos

| Métrica | Go | Python |
|---------|----|---------:|
| Uso de CPU | - | - |
| Uso de Memória | - | - |
| Threads/Goroutines | - | - |

> **Nota:** Estatísticas completas em [`results/cpu_memory_stats.md`](results/cpu_memory_stats.md)

## ✅ O que Testar

### 1. **Leitura e Limpeza de CSV Grande**
- Arquivos de diferentes tamanhos (1MB, 10MB, 100MB)
- Limpeza de dados (remoção de nulls, duplicatas)
- Transformações básicas

### 2. **Cálculos Simples**
- Média de colunas numéricas
- Somatório de grupos
- Agregações complexas
- Filtros e ordenações

### 3. **Execução Paralela de Tarefas I/O Bound**
- Simulação de chamadas de API
- Leitura de múltiplos arquivos
- Operações de rede

### 4. **Execução Paralela de Tarefas CPU Bound**
- Cálculos matemáticos intensivos
- Processamento de imagens
- Algoritmos de ordenação

## 🔧 Ferramentas Úteis

### Python
```python
# Paralelismo e Concorrência
import multiprocessing
import threading
import concurrent.futures

# Processamento de Dados
import pandas as pd
import numpy as np

# Monitoramento
import psutil
import time
import cProfile
```

### Go
```go
// Concorrência
import (
    "sync"
    "time"
    "runtime"
    _ "net/http/pprof"
)

// Processamento
import (
    "encoding/csv"
    "strconv"
    "context"
)
```

## 📂 Estrutura do Projeto

```
go-vs-python-data-processing/
├── data/
│   └── sample_dataset.csv          # Dataset de exemplo
├── go/
│   ├── benchmarks/                 # Benchmarks Go
│   ├── goroutines.go              # Testes com goroutines
│   └── process_data.go            # Processamento principal
├── python/
│   ├── benchmarks/                 # Benchmarks Python
│   ├── parallel_threads.py        # Testes com threads
│   └── process_data.py            # Processamento principal
├── results/
│   ├── cpu_memory_stats.md        # Estatísticas de recursos
│   └── time_comparison.md         # Comparação de tempos
├── go.mod                         # Dependências Go
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

## 🚀 Próximos Passos

- [ ] Implementar benchmarks automáticos
- [ ] Adicionar mais cenários de teste
- [ ] Criar gráficos de performance
- [ ] Adicionar testes com diferentes tamanhos de dataset
- [ ] Implementar medição de throughput
- [ ] Adicionar análise de escalabilidade

## 📝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

