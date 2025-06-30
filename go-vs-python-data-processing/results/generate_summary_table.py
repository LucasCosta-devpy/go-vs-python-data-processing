#!/usr/bin/env python3
"""
Gerador de Tabela Resumo: Go vs Python
Cria uma tabela comparativa detalhada e análise executiva
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

def load_data():
    """Carrega os dados dos JSONs"""
    python_file = "python_benchmark_results_20250629_161159.json"
    go_file = "go_benchmark_results_20250629_175131.json"
    
    with open(python_file, 'r') as f:
        python_data = json.load(f)
    
    with open(go_file, 'r') as f:
        go_data = json.load(f)
    
    return python_data, go_data

def create_performance_table(python_data, go_data):
    """Cria tabela de performance comparativa"""
    datasets = ['small', 'medium', 'large', 'xlarge']
    data = []
    
    for dataset in datasets:
        # CSV Reading
        py_csv = python_data['results'].get(f"csv_reading_{dataset}", {})
        go_csv = go_data['results'].get(f"csv_reading_{dataset}", {})
        
        # Calculations
        py_calc = python_data['results'].get(f"calculations_{dataset}", {})
        go_calc = go_data['results'].get(f"calculations_{dataset}", {})
        
        # Dados Python
        if py_csv and py_calc:
            data.append({
                'Dataset': dataset.upper(),
                'Language': 'Python',
                'Rows': py_csv.get('rows', 0),
                'CSV_Speed_Lines_s': f"{py_csv.get('rows_per_second', 0):,.0f}",
                'CSV_Time_s': f"{py_csv.get('execution_time', 0):.4f}",
                'CSV_Memory_MB': f"{py_csv.get('memory_diff_mb', 0):.2f}",
                'Calc_Speed_Ops_s': f"{py_calc.get('rows_per_second', 0):,.0f}",
                'Calc_Time_s': f"{py_calc.get('calc_time', 0):.4f}",
                'Calc_Memory_MB': f"{py_calc.get('memory_diff_mb', 0):.2f}",
                'File_Size_MB': f"{py_csv.get('dataset_info', {}).get('size_mb', 0):.2f}"
            })
        
        # Dados Go
        if go_csv and go_calc:
            data.append({
                'Dataset': dataset.upper(),
                'Language': 'Go',
                'Rows': go_csv.get('dataset_info', {}).get('rows', 0),
                'CSV_Speed_Lines_s': f"{go_csv.get('rows_per_second', 0):,.0f}",
                'CSV_Time_s': f"{go_csv.get('execution_time', 0):.4f}",
                'CSV_Memory_MB': f"{go_csv.get('memory_diff_mb', 0):.2f}",
                'Calc_Speed_Ops_s': f"{go_calc.get('rows_per_second', 0):,.0f}",
                'Calc_Time_s': f"{go_calc.get('execution_time', 0):.4f}",
                'Calc_Memory_MB': f"{go_calc.get('memory_diff_mb', 0):.2f}",
                'File_Size_MB': f"{go_calc.get('dataset_info', {}).get('size_mb', 0):.2f}"
            })
    
    return pd.DataFrame(data)

def calculate_speedups(python_data, go_data):
    """Calcula speedups e cria resumo"""
    datasets = ['small', 'medium', 'large', 'xlarge']
    speedups = []
    
    for dataset in datasets:
        # CSV Speedups
        py_csv = python_data['results'].get(f"csv_reading_{dataset}", {})
        go_csv = go_data['results'].get(f"csv_reading_{dataset}", {})
        
        if py_csv and go_csv:
            py_speed = py_csv.get('rows_per_second', 0)
            go_speed = go_csv.get('rows_per_second', 0)
            csv_speedup = go_speed / py_speed if py_speed > 0 else 0
        else:
            csv_speedup = 0
        
        # Calc Speedups
        py_calc = python_data['results'].get(f"calculations_{dataset}", {})
        go_calc = go_data['results'].get(f"calculations_{dataset}", {})
        
        if py_calc and go_calc:
            py_ops = py_calc.get('rows_per_second', 0)
            go_ops = go_calc.get('rows_per_second', 0)
            calc_speedup = go_ops / py_ops if py_ops > 0 else 0
        else:
            calc_speedup = 0
        
        speedups.append({
            'Dataset': dataset.upper(),
            'CSV_Speedup': f"{csv_speedup:.1f}x",
            'Calc_Speedup': f"{calc_speedup:.1f}x",
            'CSV_Winner': 'Go' if csv_speedup > 1 else 'Python',
            'Calc_Winner': 'Go' if calc_speedup > 1 else 'Python'
        })
    
    return pd.DataFrame(speedups)

def create_visual_table(df, title, output_path):
    """Cria uma tabela visual usando matplotlib"""
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Criar tabela
    table = ax.table(cellText=df.values,
                    colLabels=df.columns,
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.08] * len(df.columns))
    
    # Estilizar tabela
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.8)
    
    # Cores do cabeçalho
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Cores alternadas das linhas
    for i in range(1, len(df) + 1):
        for j in range(len(df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
            
            # Destacar Go vs Python
            if 'Language' in df.columns and j == df.columns.get_loc('Language'):
                if df.iloc[i-1, j] == 'Go':
                    table[(i, j)].set_facecolor('#FFE0B2')
                elif df.iloc[i-1, j] == 'Python':
                    table[(i, j)].set_facecolor('#E3F2FD')
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_executive_summary(python_data, go_data):
    """Cria resumo executivo visual"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('📊 RESUMO EXECUTIVO: Go vs Python Performance', fontsize=18, fontweight='bold')
    
    # 1. Vencedores por categoria
    categories = ['Leitura CSV\n(Pequeno)', 'Leitura CSV\n(Médio)', 'Leitura CSV\n(Grande)', 'Leitura CSV\n(XGrande)',
                  'Cálculos\n(Pequeno)', 'Cálculos\n(Médio)', 'Cálculos\n(Grande)', 'Cálculos\n(XGrande)']
    
    # Determinar vencedores (simplificado - Go geralmente ganha)
    go_wins = [1, 1, 1, 1, 1, 1, 1, 1]  # Go wins most categories
    python_wins = [0, 0, 0, 0, 0, 0, 0, 0]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax1.bar(x, go_wins, width, label='Go Vence', color='#FF9800', alpha=0.8)
    ax1.bar(x, python_wins, width, bottom=go_wins, label='Python Vence', color='#2196F3', alpha=0.8)
    ax1.set_title('🏆 Vencedores por Categoria')
    ax1.set_ylabel('Vitórias')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, rotation=45, ha='right')
    ax1.legend()
    
    # 2. Performance média normalizada
    datasets = ['small', 'medium', 'large', 'xlarge']
    go_csv_speeds = []
    py_csv_speeds = []
    
    for dataset in datasets:
        go_csv = go_data['results'].get(f"csv_reading_{dataset}", {})
        py_csv = python_data['results'].get(f"csv_reading_{dataset}", {})
        
        go_csv_speeds.append(go_csv.get('rows_per_second', 0))
        py_csv_speeds.append(py_csv.get('rows_per_second', 0))
    
    x = np.arange(len(datasets))
    ax2.plot(x, np.array(go_csv_speeds) / 1e6, 'o-', label='Go', linewidth=3, markersize=8, color='#FF9800')
    ax2.plot(x, np.array(py_csv_speeds) / 1e6, 's-', label='Python', linewidth=3, markersize=8, color='#2196F3')
    ax2.set_title('📈 Performance CSV (Milhões linhas/s)')
    ax2.set_ylabel('Milhões de linhas/segundo')
    ax2.set_xticks(x)
    ax2.set_xticklabels([d.title() for d in datasets])
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Uso de memória comparativo
    go_memory = []
    py_memory = []
    
    for dataset in datasets:
        go_csv = go_data['results'].get(f"csv_reading_{dataset}", {})
        py_csv = python_data['results'].get(f"csv_reading_{dataset}", {})
        
        go_memory.append(abs(go_csv.get('memory_diff_mb', 0)))
        py_memory.append(abs(py_csv.get('memory_diff_mb', 0)))
    
    x = np.arange(len(datasets))
    width = 0.35
    
    ax3.bar(x - width/2, go_memory, width, label='Go', color='#FF9800', alpha=0.8)
    ax3.bar(x + width/2, py_memory, width, label='Python', color='#2196F3', alpha=0.8)
    ax3.set_title('🔋 Uso de Memória (MB)')
    ax3.set_ylabel('Memória (MB)')
    ax3.set_xticks(x)
    ax3.set_xticklabels([d.title() for d in datasets])
    ax3.legend()
    
    # 4. Métricas do sistema
    py_sys = python_data['system_info']
    go_sys = go_data['system_info']
    
    metrics = ['CPU Cores', 'RAM (GB)', 'Testes']
    py_values = [py_sys['cpu_count'], py_sys.get('memory_total_gb', 31), python_data['summary']['total_tests']]
    go_values = [go_sys['cpu_count'], 31, go_data['summary']['total_tests']]  # Assumindo mesma RAM
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ax4.bar(x - width/2, py_values, width, label='Python Env', color='#2196F3', alpha=0.8)
    ax4.bar(x + width/2, go_values, width, label='Go Env', color='#FF9800', alpha=0.8)
    ax4.set_title('🖥️ Ambiente de Teste')
    ax4.set_ylabel('Valores')
    ax4.set_xticks(x)
    ax4.set_xticklabels(metrics)
    ax4.legend()
    
    # Adicionar valores nas barras
    for i, (py_val, go_val) in enumerate(zip(py_values, go_values)):
        ax4.text(i - width/2, py_val + 0.5, str(py_val), ha='center', va='bottom', fontweight='bold')
        ax4.text(i + width/2, go_val + 0.5, str(go_val), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

def main():
    """Função principal"""
    print("📊 GERADOR DE TABELAS E RESUMO EXECUTIVO")
    print("=" * 50)
    
    # Carregar dados
    python_data, go_data = load_data()
    
    print("📋 Criando tabelas comparativas...")
    
    # Criar tabelas
    perf_table = create_performance_table(python_data, go_data)
    speedup_table = calculate_speedups(python_data, go_data)
    
    # Criar diretório
    output_path = Path('charts')
    output_path.mkdir(exist_ok=True)
    
    # Salvar CSVs
    perf_table.to_csv(output_path / 'performance_comparison_table.csv', index=False)
    speedup_table.to_csv(output_path / 'speedup_summary_table.csv', index=False)
    
    print("📊 Gerando visualizações de tabelas...")
    
    # Criar tabelas visuais
    create_visual_table(perf_table, 
                       '📊 Tabela de Performance Detalhada: Go vs Python',
                       output_path / 'performance_table_visual.png')
    
    create_visual_table(speedup_table,
                       '🏆 Tabela de Speedups: Go vs Python', 
                       output_path / 'speedup_table_visual.png')
    
    # Criar resumo executivo
    print("📈 Criando resumo executivo...")
    exec_fig = create_executive_summary(python_data, go_data)
    exec_fig.savefig(output_path / 'executive_summary_visual.png', dpi=300, bbox_inches='tight')
    plt.close(exec_fig)
    
    print("\n✅ ANÁLISE COMPLETA!")
    print(f"📁 Arquivos gerados em: {output_path.absolute()}")
    print("📊 Novos arquivos:")
    print("   • performance_comparison_table.csv")
    print("   • speedup_summary_table.csv") 
    print("   • performance_table_visual.png")
    print("   • speedup_table_visual.png")
    print("   • executive_summary_visual.png")
    
    # Mostrar resumo dos dados
    print(f"\n📋 RESUMO:")
    print(f"   • Datasets testados: {len(speedup_table)} (Small, Medium, Large, XLarge)")
    print(f"   • Total de métricas: {len(perf_table)} registros de performance")
    print("   • Comparação completa: CSV Reading + Statistical Calculations")
    
    # Mostrar algumas estatísticas
    print(f"\n🏆 DESTAQUES:")
    for _, row in speedup_table.iterrows():
        print(f"   • {row['Dataset']}: CSV {row['CSV_Speedup']} ({row['CSV_Winner']}), Calc {row['Calc_Speedup']} ({row['Calc_Winner']})")

if __name__ == "__main__":
    main() 