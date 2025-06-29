import pandas as pd
import time
import psutil
import os
import json
from datetime import datetime
# Imports locais
import sys
sys.path.append('.')

# Importar funções dos outros módulos diretamente
def generate_large_dataset(num_rows=10000, filename='large_dataset.csv'):
    """Gera um CSV com num_rows linhas baseado no formato do sample_dataset.csv"""
    import csv
    import random
    
    data_dir = '../data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'value'])
        
        for i in range(1, num_rows + 1):
            value = random.randint(50, 5000)
            writer.writerow([i, value])
    
    return filepath

class BenchmarkSuite:
    """
    Suite completo de benchmarks para comparação de performance
    """
    
    def __init__(self):
        self.results = {}
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """Coleta informações do sistema"""
        return {
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'python_version': f"{psutil.version_info}",
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_test_datasets(self):
        """
        Gera datasets de diferentes tamanhos para teste
        """
        datasets = [
            {'name': 'small', 'rows': 1000, 'filename': 'dataset_1k.csv'},
            {'name': 'medium', 'rows': 10000, 'filename': 'dataset_10k.csv'},
            {'name': 'large', 'rows': 100000, 'filename': 'dataset_100k.csv'},
            {'name': 'xlarge', 'rows': 500000, 'filename': 'dataset_500k.csv'},
        ]
        
        print("🔄 GERANDO DATASETS DE TESTE...")
        print("="*50)
        
        for dataset in datasets:
            print(f"📊 Gerando {dataset['name']}: {dataset['rows']:,} linhas...")
            filepath = generate_large_dataset(
                num_rows=dataset['rows'], 
                filename=dataset['filename']
            )
            dataset['filepath'] = filepath
            
            # Verificar tamanho
            file_size = os.path.getsize(filepath)
            dataset['size_mb'] = file_size / (1024 * 1024)
            print(f"   ✅ Gerado: {file_size:,} bytes ({dataset['size_mb']:.2f} MB)")
        
        return datasets
    
    def benchmark_csv_reading(self, datasets):
        """
        Benchmark de leitura de CSV
        """
        print(f"\n{'='*60}")
        print("BENCHMARK: LEITURA DE CSV")
        print(f"{'='*60}")
        
        results = {}
        
        for dataset in datasets:
            print(f"\n🎯 Testando {dataset['name']} ({dataset['rows']:,} linhas)")
            
            if os.path.exists(dataset['filepath']):
                # Medir recursos antes
                process = psutil.Process()
                memory_before = process.memory_info().rss / (1024 * 1024)
                
                # Medir tempo de leitura
                start_time = time.time()
                df = pd.read_csv(dataset['filepath'])
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Medir recursos depois
                memory_after = process.memory_info().rss / (1024 * 1024)
                memory_diff = memory_after - memory_before
                
                print(f"   ⏱️ Tempo de leitura: {execution_time:.4f}s")
                print(f"   🚀 Velocidade: {len(df)/execution_time:,.0f} linhas/s")
                print(f"   🔋 Memória usada: {memory_diff:+.1f} MB")
                
                # Salvar resultado
                key = f"csv_reading_{dataset['name']}"
                results[key] = {
                    'file': dataset['filename'],
                    'rows': len(df),
                    'execution_time': execution_time,
                    'rows_per_second': len(df) / execution_time,
                    'memory_diff_mb': memory_diff,
                    'dataset_info': dataset
                }
        
        return results
    
    def benchmark_calculations(self, datasets):
        """
        Benchmark de cálculos estatísticos
        """
        print(f"\n{'='*60}")
        print("BENCHMARK: CÁLCULOS ESTATÍSTICOS")
        print(f"{'='*60}")
        
        results = {}
        
        for dataset in datasets:
            if not os.path.exists(dataset['filepath']):
                continue
                
            print(f"\n🧮 Calculando {dataset['name']} ({dataset['rows']:,} linhas)")
            
            # Carregar dados
            start_load = time.time()
            df = pd.read_csv(dataset['filepath'])
            load_time = time.time() - start_load
            
            # Medir recursos antes
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 * 1024)
            
            # Executar cálculos
            start_calc = time.time()
            
            calculations = {
                'sum': df['value'].sum(),
                'mean': df['value'].mean(),
                'median': df['value'].median(),
                'std': df['value'].std(),
                'min': df['value'].min(),
                'max': df['value'].max(),
                'quantile_25': df['value'].quantile(0.25),
                'quantile_75': df['value'].quantile(0.75),
                'count': len(df),
                'unique_count': df['value'].nunique()
            }
            
            calc_time = time.time() - start_calc
            
            # Medir recursos depois
            memory_after = process.memory_info().rss / (1024 * 1024)
            memory_diff = memory_after - memory_before
            
            print(f"   ⏱️ Tempo de cálculo: {calc_time:.4f}s")
            print(f"   🔋 Memória usada: {memory_diff:+.1f} MB")
            print(f"   📊 Resultados: {len(calculations)} métricas calculadas")
            
            results[f"calculations_{dataset['name']}"] = {
                'dataset_info': dataset,
                'load_time': load_time,
                'calc_time': calc_time,
                'memory_diff_mb': memory_diff,
                'calculations': calculations,
                'rows_per_second': len(df) / calc_time
            }
        
        return results
    
    def benchmark_parallel_processing(self, datasets):
        """
        Benchmark de processamento paralelo simplificado
        """
        print(f"\n{'='*60}")
        print("BENCHMARK: PROCESSAMENTO PARALELO")
        print(f"{'='*60}")
        
        results = {}
        
        # Testar apenas com datasets médio (para não demorar muito)
        test_datasets = [d for d in datasets if d['name'] in ['medium']]
        
        for dataset in test_datasets:
            if not os.path.exists(dataset['filepath']):
                continue
                
            print(f"\n🔄 Processamento paralelo: {dataset['name']} ({dataset['rows']:,} linhas)")
            
            # Carregar dados
            df = pd.read_csv(dataset['filepath'])
            data = df['value'].tolist()
            
            # Função simples de processamento
            def process_data_sequential(data):
                return [x * 2 + 1 for x in data]
            
            def process_data_chunk(chunk):
                return [x * 2 + 1 for x in chunk]
            
            # Teste sequencial
            start_time = time.time()
            result_seq = process_data_sequential(data)
            sequential_time = time.time() - start_time
            
            # Teste com threads
            from concurrent.futures import ThreadPoolExecutor
            
            start_time = time.time()
            chunk_size = len(data) // 4
            chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                thread_results = list(executor.map(process_data_chunk, chunks))
            
            # Combinar resultados
            result_parallel = []
            for chunk_result in thread_results:
                result_parallel.extend(chunk_result)
                
            parallel_time = time.time() - start_time
            
            print(f"   ⏱️ Sequencial: {sequential_time:.4f}s")
            print(f"   ⏱️ Paralelo (threads): {parallel_time:.4f}s")
            print(f"   🚀 Speedup: {sequential_time/parallel_time:.2f}x")
            
            # Salvar resultados
            results[f"parallel_sequential_{dataset['name']}"] = {
                'method': 'sequential',
                'execution_time': sequential_time,
                'dataset_info': dataset
            }
            
            results[f"parallel_threads_{dataset['name']}"] = {
                'method': 'threads',
                'execution_time': parallel_time,
                'dataset_info': dataset
            }
        
        return results
    
    def generate_performance_report(self, all_results):
        """
        Gera relatório de performance
        """
        print(f"\n{'='*60}")
        print("RELATÓRIO DE PERFORMANCE")
        print(f"{'='*60}")
        
        # Informações do sistema
        print(f"\n🖥️ INFORMAÇÕES DO SISTEMA:")
        print(f"   • CPU Cores (físicos): {self.system_info['cpu_count']}")
        print(f"   • CPU Cores (lógicos): {self.system_info['cpu_count_logical']}")
        print(f"   • Memória Total: {self.system_info['memory_total_gb']:.1f} GB")
        print(f"   • Data/Hora: {self.system_info['timestamp']}")
        
        # Resumo de leitura de CSV
        print(f"\n📊 PERFORMANCE DE LEITURA DE CSV:")
        csv_results = {k: v for k, v in all_results.items() if k.startswith('csv_reading_')}
        
        if csv_results:
            print(f"{'Dataset':<15} {'Linhas':<10} {'Tamanho (MB)':<12} {'Tempo (s)':<10} {'Velocidade (linhas/s)':<20}")
            print("-" * 75)
            
            for key, result in csv_results.items():
                dataset_name = result['dataset_info']['name']
                rows = result['rows']
                size_mb = result['dataset_info']['size_mb']
                time_s = result['execution_time']
                speed = result['rows_per_second']
                
                print(f"{dataset_name:<15} {rows:<10,} {size_mb:<12.2f} {time_s:<10.4f} {speed:<20,.0f}")
        
        # Resumo de cálculos
        print(f"\n🧮 PERFORMANCE DE CÁLCULOS:")
        calc_results = {k: v for k, v in all_results.items() if k.startswith('calculations_')}
        
        if calc_results:
            print(f"{'Dataset':<15} {'Linhas':<10} {'Tempo (s)':<10} {'Velocidade (linhas/s)':<20}")
            print("-" * 60)
            
            for key, result in calc_results.items():
                dataset_name = result['dataset_info']['name']
                rows = result['dataset_info']['rows']
                time_s = result['calc_time']
                speed = result['rows_per_second']
                
                print(f"{dataset_name:<15} {rows:<10,} {time_s:<10.4f} {speed:<20,.0f}")
        
        # Resumo de paralelismo
        print(f"\n🔄 PERFORMANCE DE PARALELISMO:")
        parallel_results = {k: v for k, v in all_results.items() if k.startswith('parallel_')}
        
        if parallel_results:
            print(f"{'Método':<20} {'Dataset':<10} {'Tempo (s)':<10} {'Speedup':<10}")
            print("-" * 55)
            
            # Agrupar por dataset
            by_dataset = {}
            for key, result in parallel_results.items():
                parts = key.split('_')
                method = parts[1]
                dataset_name = parts[2]
                
                if dataset_name not in by_dataset:
                    by_dataset[dataset_name] = {}
                by_dataset[dataset_name][method] = result
            
            for dataset_name, methods in by_dataset.items():
                if 'sequential' in methods and 'threads' in methods:
                    seq_time = methods['sequential']['execution_time']
                    thread_time = methods['threads']['execution_time']
                    speedup = seq_time / thread_time
                    
                    print(f"{'Sequential':<20} {dataset_name:<10} {seq_time:<10.4f} {'1.00x':<10}")
                    print(f"{'Threads':<20} {dataset_name:<10} {thread_time:<10.4f} {speedup:<10.2f}")
                    print("-" * 55)
    
    def save_results_to_file(self, all_results):
        """
        Salva resultados em arquivo JSON
        """
        # Criar diretório results se não existir
        results_dir = '../results'
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # Preparar dados para JSON
        output_data = {
            'system_info': self.system_info,
            'results': all_results,
            'summary': {
                'total_tests': len(all_results),
                'csv_reading_tests': len([k for k in all_results.keys() if k.startswith('csv_reading_')]),
                'calculation_tests': len([k for k in all_results.keys() if k.startswith('calculations_')]),
                'parallel_tests': len([k for k in all_results.keys() if k.startswith('parallel_')])
            }
        }
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'python_benchmark_results_{timestamp}.json'
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n💾 Resultados salvos em: {filepath}")
        return filepath
    
    def run_full_benchmark(self):
        """
        Executa o benchmark completo
        """
        print("🚀 INICIANDO BENCHMARK SUITE COMPLETO - PYTHON")
        print("=" * 60)
        
        # Gerar datasets
        datasets = self.generate_test_datasets()
        
        all_results = {}
        
        # Executar benchmarks
        print(f"\n🔍 EXECUTANDO BENCHMARKS...")
        
        # 1. Leitura de CSV
        csv_results = self.benchmark_csv_reading(datasets)
        all_results.update(csv_results)
        
        # 2. Cálculos estatísticos
        calc_results = self.benchmark_calculations(datasets)
        all_results.update(calc_results)
        
        # 3. Processamento paralelo
        parallel_results = self.benchmark_parallel_processing(datasets)
        all_results.update(parallel_results)
        
        # Gerar relatório
        self.generate_performance_report(all_results)
        
        # Salvar resultados
        self.save_results_to_file(all_results)
        
        print(f"\n✅ BENCHMARK SUITE CONCLUÍDO!")
        print(f"📊 Total de testes executados: {len(all_results)}")
        
        return all_results

def main():
    """
    Função principal
    """
    suite = BenchmarkSuite()
    results = suite.run_full_benchmark()
    
    return results

if __name__ == "__main__":
    main() 