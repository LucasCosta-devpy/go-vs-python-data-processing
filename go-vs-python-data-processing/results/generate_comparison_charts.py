#!/usr/bin/env python3
"""
Gerador de Gráficos de Comparação: Go vs Python
Analisa os resultados de performance e gera visualizações comparativas
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo dos gráficos
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

def load_benchmark_data(python_file, go_file):
    """Carrega os dados dos arquivos JSON"""
    print("📊 Carregando dados de performance...")
    
    with open(python_file, 'r') as f:
        python_data = json.load(f)
    
    with open(go_file, 'r') as f:
        go_data = json.load(f)
        
    print(f"✅ Python: {len(python_data['results'])} testes")
    print(f"✅ Go: {len(go_data['results'])} testes")
    
    return python_data, go_data

def extract_csv_performance_data(python_data, go_data):
    """Extrai dados de performance de leitura CSV"""
    datasets = ['small', 'medium', 'large', 'xlarge']
    data = []
    
    for dataset in datasets:
        # Python data
        py_key = f"csv_reading_{dataset}"
        if py_key in python_data['results']:
            py_result = python_data['results'][py_key]
            data.append({
                'Dataset': dataset.title(),
                'Language': 'Python',
                'Rows': py_result['rows'],
                'Execution_Time': py_result['execution_time'],
                'Rows_Per_Second': py_result['rows_per_second'],
                'Memory_MB': py_result['memory_diff_mb'],
                'File_Size_MB': py_result['dataset_info']['size_mb']
            })
        
        # Go data
        go_key = f"csv_reading_{dataset}"
        if go_key in go_data['results']:
            go_result = go_data['results'][go_key]
            data.append({
                'Dataset': dataset.title(),
                'Language': 'Go',
                'Rows': go_result['dataset_info']['rows'],
                'Execution_Time': go_result['execution_time'],
                'Rows_Per_Second': go_result['rows_per_second'],
                'Memory_MB': go_result['memory_diff_mb'],
                'File_Size_MB': go_result['dataset_info']['size_mb']
            })
    
    return pd.DataFrame(data)

def extract_calculation_performance_data(python_data, go_data):
    """Extrai dados de performance de cálculos"""
    datasets = ['small', 'medium', 'large', 'xlarge']
    data = []
    
    for dataset in datasets:
        # Python data
        py_key = f"calculations_{dataset}"
        if py_key in python_data['results']:
            py_result = python_data['results'][py_key]
            data.append({
                'Dataset': dataset.title(),
                'Language': 'Python',
                'Rows': py_result['dataset_info']['rows'],
                'Execution_Time': py_result['calc_time'],
                'Ops_Per_Second': py_result['rows_per_second'],
                'Memory_MB': py_result['memory_diff_mb']
            })
        
        # Go data
        go_key = f"calculations_{dataset}"
        if go_key in go_data['results']:
            go_result = go_data['results'][go_key]
            data.append({
                'Dataset': dataset.title(),
                'Language': 'Go',
                'Rows': go_result['dataset_info']['rows'],
                'Execution_Time': go_result['execution_time'],
                'Ops_Per_Second': go_result['rows_per_second'],
                'Memory_MB': go_result['memory_diff_mb']
            })
    
    return pd.DataFrame(data)

def create_csv_performance_chart(df):
    """Cria gráfico de performance de leitura CSV"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('📊 Performance de Leitura CSV: Go vs Python', fontsize=16, fontweight='bold')
    
    # 1. Velocidade (linhas/segundo)
    sns.barplot(data=df, x='Dataset', y='Rows_Per_Second', hue='Language', ax=ax1)
    ax1.set_title('🚀 Velocidade de Leitura (linhas/segundo)')
    ax1.set_ylabel('Linhas/segundo')
    ax1.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    
    # 2. Tempo de execução
    sns.barplot(data=df, x='Dataset', y='Execution_Time', hue='Language', ax=ax2)
    ax2.set_title('⏱️ Tempo de Execução (segundos)')
    ax2.set_ylabel('Segundos')
    
    # 3. Uso de memória
    sns.barplot(data=df, x='Dataset', y='Memory_MB', hue='Language', ax=ax3)
    ax3.set_title('🔋 Uso de Memória (MB)')
    ax3.set_ylabel('MB')
    
    # 4. Eficiência (linhas/segundo por MB de arquivo)
    df['Efficiency'] = df['Rows_Per_Second'] / df['File_Size_MB']
    sns.barplot(data=df, x='Dataset', y='Efficiency', hue='Language', ax=ax4)
    ax4.set_title('📈 Eficiência (linhas/s por MB de arquivo)')
    ax4.set_ylabel('Eficiência')
    ax4.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    
    plt.tight_layout()
    return fig

def create_calculation_performance_chart(df):
    """Cria gráfico de performance de cálculos"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('🧮 Performance de Cálculos Estatísticos: Go vs Python', fontsize=16, fontweight='bold')
    
    # 1. Velocidade (operações/segundo)
    sns.barplot(data=df, x='Dataset', y='Ops_Per_Second', hue='Language', ax=ax1)
    ax1.set_title('🚀 Velocidade de Cálculo (ops/segundo)')
    ax1.set_ylabel('Operações/segundo')
    ax1.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    
    # 2. Tempo de execução
    sns.barplot(data=df, x='Dataset', y='Execution_Time', hue='Language', ax=ax2)
    ax2.set_title('⏱️ Tempo de Execução (segundos)')
    ax2.set_ylabel('Segundos')
    
    # 3. Uso de memória
    sns.barplot(data=df, x='Dataset', y='Memory_MB', hue='Language', ax=ax3)
    ax3.set_title('🔋 Uso de Memória (MB)')
    ax3.set_ylabel('MB')
    
    # 4. Throughput por linha de dados
    df['Throughput_Per_Row'] = df['Ops_Per_Second'] / df['Rows']
    sns.barplot(data=df, x='Dataset', y='Throughput_Per_Row', hue='Language', ax=ax4)
    ax4.set_title('📊 Throughput por Linha')
    ax4.set_ylabel('Ops/segundo por linha')
    
    plt.tight_layout()
    return fig

def create_speedup_comparison(csv_df, calc_df):
    """Cria gráfico de speedup Go vs Python"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('🏆 Speedup: Go vs Python', fontsize=16, fontweight='bold')
    
    # Calcular speedup para CSV
    csv_speedup = []
    for dataset in ['Small', 'Medium', 'Large', 'Xlarge']:
        go_row = csv_df[(csv_df['Dataset'] == dataset) & (csv_df['Language'] == 'Go')]
        py_row = csv_df[(csv_df['Dataset'] == dataset) & (csv_df['Language'] == 'Python')]
        
        if not go_row.empty and not py_row.empty:
            go_speed = go_row['Rows_Per_Second'].iloc[0]
            py_speed = py_row['Rows_Per_Second'].iloc[0]
            speedup = go_speed / py_speed if py_speed > 0 else 0
            csv_speedup.append({'Dataset': dataset, 'Speedup': speedup})
    
    # Calcular speedup para cálculos
    calc_speedup = []
    for dataset in ['Small', 'Medium', 'Large', 'Xlarge']:
        go_row = calc_df[(calc_df['Dataset'] == dataset) & (calc_df['Language'] == 'Go')]
        py_row = calc_df[(calc_df['Dataset'] == dataset) & (calc_df['Language'] == 'Python')]
        
        if not go_row.empty and not py_row.empty:
            go_ops = go_row['Ops_Per_Second'].iloc[0]
            py_ops = py_row['Ops_Per_Second'].iloc[0]
            speedup = go_ops / py_ops if py_ops > 0 else 0
            calc_speedup.append({'Dataset': dataset, 'Speedup': speedup})
    
    # Plotar speedups
    if csv_speedup:
        csv_speedup_df = pd.DataFrame(csv_speedup)
        bars1 = ax1.bar(csv_speedup_df['Dataset'], csv_speedup_df['Speedup'], 
                       color=['#ff7f0e' if x > 1 else '#d62728' for x in csv_speedup_df['Speedup']])
        ax1.set_title('📊 Speedup - Leitura CSV')
        ax1.set_ylabel('Speedup (Go/Python)')
        ax1.axhline(y=1, color='black', linestyle='--', alpha=0.5)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars1, csv_speedup_df['Speedup']):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{value:.1f}x', ha='center', va='bottom', fontweight='bold')
    
    if calc_speedup:
        calc_speedup_df = pd.DataFrame(calc_speedup)
        bars2 = ax2.bar(calc_speedup_df['Dataset'], calc_speedup_df['Speedup'],
                       color=['#ff7f0e' if x > 1 else '#d62728' for x in calc_speedup_df['Speedup']])
        ax2.set_title('🧮 Speedup - Cálculos')
        ax2.set_ylabel('Speedup (Go/Python)')
        ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars2, calc_speedup_df['Speedup']):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.1f}x', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig

def main():
    """Função principal"""
    print("🎯 GERADOR DE GRÁFICOS: Go vs Python Performance")
    print("=" * 60)
    
    # Arquivos de entrada
    python_file = "results\python_benchmark_results_20250629_161159.json"
    go_file = "results\go_benchmark_results_20250629_175131.json"
    
    # Verificar se arquivos existem
    if not Path(python_file).exists():
        print(f"❌ Arquivo não encontrado: {python_file}")
        return
    
    if not Path(go_file).exists():
        print(f"❌ Arquivo não encontrado: {go_file}")
        return
    
    # Carregar dados
    python_data, go_data = load_benchmark_data(python_file, go_file)
    
    # Extrair dados
    print("\n📊 Extraindo dados de performance...")
    csv_df = extract_csv_performance_data(python_data, go_data)
    calc_df = extract_calculation_performance_data(python_data, go_data)
    
    # Criar diretório de output
    output_path = Path('charts')
    output_path.mkdir(exist_ok=True)
    
    print(f"\n🎨 Gerando gráficos em {output_path}...")
    
    # 1. Performance de CSV
    print("   📈 Gráfico de performance CSV...")
    fig1 = create_csv_performance_chart(csv_df)
    fig1.savefig(output_path / 'csv_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close(fig1)
    
    # 2. Performance de cálculos
    print("   🧮 Gráfico de performance de cálculos...")
    fig2 = create_calculation_performance_chart(calc_df)
    fig2.savefig(output_path / 'calculation_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close(fig2)
    
    # 3. Speedup
    print("   🏆 Gráfico de speedup...")
    fig3 = create_speedup_comparison(csv_df, calc_df)
    fig3.savefig(output_path / 'speedup_comparison.png', dpi=300, bbox_inches='tight')
    plt.close(fig3)
    
    print(f"\n✅ GRÁFICOS GERADOS COM SUCESSO!")
    print(f"📁 Localização: {output_path.absolute()}")
    print("📊 Arquivos criados:")
    print("   • csv_performance_comparison.png")
    print("   • calculation_performance_comparison.png") 
    print("   • speedup_comparison.png")
    
    # Imprimir resumo dos dados
    print(f"\n📊 RESUMO DOS DADOS EXTRAÍDOS:")
    print(f"   • CSV Performance: {len(csv_df)} registros")
    print(f"   • Calculation Performance: {len(calc_df)} registros")
    
    print(f"\n🎉 ANÁLISE COMPLETA FINALIZADA!")

if __name__ == "__main__":
    main() 