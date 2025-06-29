import pandas as pd
import time
import psutil
import os
from pathlib import Path

class DataProcessor:
    """
    Classe para processar dados e medir performance
    """
    
    def __init__(self):
        self.process = psutil.Process()
        self.results = {}
    
    def measure_resources(self):
        """Mede uso atual de CPU e memória"""
        return {
            'cpu_percent': self.process.cpu_percent(),
            'memory_mb': self.process.memory_info().rss / 1024 / 1024,
            'memory_percent': self.process.memory_percent()
        }
    
    def read_csv_with_timing(self, filepath, method='pandas'):
        """
        Lê CSV e mede tempo de execução e recursos
        """
        print(f"\n{'='*50}")
        print(f"LENDO CSV: {os.path.basename(filepath)}")
        print(f"Método: {method}")
        print(f"{'='*50}")
        
        # Verificar se arquivo existe
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            return None
        
        # Informações do arquivo
        file_size = os.path.getsize(filepath)
        print(f"📁 Tamanho do arquivo: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Recursos iniciais
        resources_before = self.measure_resources()
        print(f"🔋 Recursos ANTES - CPU: {resources_before['cpu_percent']:.1f}% | "
              f"Memória: {resources_before['memory_mb']:.1f} MB ({resources_before['memory_percent']:.1f}%)")
        
        # Medir tempo de leitura
        start_time = time.time()
        
        try:
            if method == 'pandas':
                df = pd.read_csv(filepath)
            else:
                # Método alternativo usando csv padrão
                import csv
                data = []
                with open(filepath, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    data = list(reader)
                df = pd.DataFrame(data)
                df['value'] = pd.to_numeric(df['value'])
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Recursos finais
            resources_after = self.measure_resources()
            
            # Informações do dataset
            print(f"\n📊 DADOS CARREGADOS:")
            print(f"   • Linhas: {len(df):,}")
            print(f"   • Colunas: {len(df.columns)}")
            print(f"   • Colunas: {list(df.columns)}")
            
            # Resultados de performance
            print(f"\n⏱️  PERFORMANCE:")
            print(f"   • Tempo de execução: {execution_time:.4f} segundos")
            print(f"   • Velocidade: {len(df)/execution_time:,.0f} linhas/segundo")
            
            print(f"\n🔋 RECURSOS DEPOIS - CPU: {resources_after['cpu_percent']:.1f}% | "
                  f"Memória: {resources_after['memory_mb']:.1f} MB ({resources_after['memory_percent']:.1f}%)")
            
            memory_diff = resources_after['memory_mb'] - resources_before['memory_mb']
            print(f"   • Diferença de memória: {memory_diff:+.1f} MB")
            
            # Salvar resultados
            result = {
                'file': os.path.basename(filepath),
                'method': method,
                'file_size_mb': file_size / 1024 / 1024,
                'rows': len(df),
                'execution_time': execution_time,
                'rows_per_second': len(df) / execution_time,
                'memory_before_mb': resources_before['memory_mb'],
                'memory_after_mb': resources_after['memory_mb'],
                'memory_diff_mb': memory_diff
            }
            
            self.results[f"{method}_{os.path.basename(filepath)}"] = result
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return None
    
    def basic_calculations(self, df):
        """
        Realiza cálculos básicos e mede performance
        """
        if df is None:
            print("❌ DataFrame vazio, pulando cálculos")
            return
        
        print(f"\n{'='*50}")
        print("EXECUTANDO CÁLCULOS BÁSICOS")
        print(f"{'='*50}")
        
        resources_before = self.measure_resources()
        start_time = time.time()
        
        try:
            # Cálculos básicos
            calculations = {
                'soma_total': df['value'].sum(),
                'media': df['value'].mean(),
                'mediana': df['value'].median(),
                'min_valor': df['value'].min(),
                'max_valor': df['value'].max(),
                'desvio_padrao': df['value'].std(),
                'count': len(df)
            }
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            resources_after = self.measure_resources()
            memory_diff = resources_after['memory_mb'] - resources_before['memory_mb']
            
            print(f"\n📈 RESULTADOS DOS CÁLCULOS:")
            for key, value in calculations.items():
                if isinstance(value, float):
                    print(f"   • {key.replace('_', ' ').title()}: {value:,.2f}")
                else:
                    print(f"   • {key.replace('_', ' ').title()}: {value:,}")
            
            print(f"\n⏱️  PERFORMANCE CÁLCULOS:")
            print(f"   • Tempo: {execution_time:.4f} segundos")
            print(f"   • Memória extra: {memory_diff:+.1f} MB")
            
            return calculations
            
        except Exception as e:
            print(f"❌ Erro nos cálculos: {e}")
            return None
    
    def compare_reading_methods(self, filepath):
        """
        Compara diferentes métodos de leitura
        """
        print(f"\n{'='*60}")
        print("COMPARAÇÃO DE MÉTODOS DE LEITURA")
        print(f"{'='*60}")
        
        methods = ['pandas']  # Pode adicionar mais métodos depois
        
        for method in methods:
            df = self.read_csv_with_timing(filepath, method)
            if df is not None:
                self.basic_calculations(df)
        
        return self.results
    
    def print_summary(self):
        """
        Imprime resumo dos resultados
        """
        if not self.results:
            print("❌ Nenhum resultado para mostrar")
            return
        
        print(f"\n{'='*60}")
        print("RESUMO DOS RESULTADOS")
        print(f"{'='*60}")
        
        for key, result in self.results.items():
            print(f"\n📊 {key}:")
            print(f"   • Arquivo: {result['file']}")
            print(f"   • Tamanho: {result['file_size_mb']:.2f} MB")
            print(f"   • Linhas: {result['rows']:,}")
            print(f"   • Tempo: {result['execution_time']:.4f}s")
            print(f"   • Velocidade: {result['rows_per_second']:,.0f} linhas/s")
            print(f"   • Memória usada: {result['memory_diff_mb']:+.1f} MB")

def main():
    """
    Função principal
    """
    print("🚀 INICIANDO TESTE DE PERFORMANCE - PYTHON")
    print("="*60)
    
    processor = DataProcessor()
    
    # Caminhos dos arquivos
    large_dataset_path = '../data/large_dataset.csv'
    sample_dataset_path = '../data/sample_dataset.csv'
    
    # Verificar se o dataset grande existe
    if not os.path.exists(large_dataset_path):
        print(f"⚠️  Dataset grande não encontrado: {large_dataset_path}")
        print("🔄 Gerando dataset...")
        
        # Importar e executar gerador
        from generate_large_dataset import generate_large_dataset
        generate_large_dataset()
    
    # Testar com dataset grande
    if os.path.exists(large_dataset_path):
        print(f"\n🎯 TESTANDO COM DATASET GRANDE")
        processor.compare_reading_methods(large_dataset_path)
    
    # Testar com dataset pequeno para comparação
    if os.path.exists(sample_dataset_path):
        print(f"\n🎯 TESTANDO COM DATASET PEQUENO (comparação)")
        processor.compare_reading_methods(sample_dataset_path)
    
    # Mostrar resumo
    processor.print_summary()
    
    print(f"\n✅ TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
