import os

# Estrutura de diretórios e arquivos
structure = {
    "go-vs-python-data-processing": {
        "python": {
            "process_data.py": "",
            "parallel_threads.py": "",
            "benchmarks": {}
        },
        "go": {
            "process_data.go": "",
            "goroutines.go": "",
            "benchmarks": {}
        },
        "data": {
            "sample_dataset.csv": "id,value\n1,100\n2,200\n"
        },
        "results": {
            "time_comparison.md": "# Tempo de Execução - Comparação\n\n",
            "cpu_memory_stats.md": "# Uso de CPU e Memória\n\n"
        },
        "README.md": "# Go vs Python - Data Processing Performance\n\n",
        "requirements.txt": "pandas\npsutil\n",
        "go.mod": "module go-vs-python-data-processing\n"
    }
}

# Função para criar a estrutura
def create_structure(base_path, struct):
    for name, content in struct.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

# Criar tudo
create_structure(".", structure)

print("Estrutura do projeto criada com sucesso!")
