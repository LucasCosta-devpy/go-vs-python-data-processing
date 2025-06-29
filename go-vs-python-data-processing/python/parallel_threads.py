import pandas as pd
import time
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing
from multiprocessing import Pool

class ParallelProcessor:
    """
    Classe para testar processamento paralelo
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
    
    def process_chunk(self, chunk_data):
        """
        Processa um chunk de dados (simulação de trabalho CPU-intensivo)
        """
        chunk_id, data = chunk_data
        
        # Simular processamento CPU-intensivo
        result = []
        for value in data:
            # Operações matemáticas
            processed = (value ** 2 + value * 3 + 17) % 1000
            result.append(processed)
        
        return {
            'chunk_id': chunk_id,
            'original_sum': sum(data),
            'processed_sum': sum(result),
            'count': len(data)
        }
    
    def io_bound_task(self, task_id):
        """
        Simula tarefa I/O bound (como chamadas de API)
        """
        import time
        import random
        
        # Simular delay de I/O
        delay = random.uniform(0.1, 0.3)
        time.sleep(delay)
        
        return {
            'task_id': task_id,
            'delay': delay,
            'result': f"Task {task_id} completed"
        }
    
    def sequential_processing(self, data, num_chunks=4):
        """
        Processamento sequencial
        """
        print(f"\n{'='*50}")
        print("PROCESSAMENTO SEQUENCIAL")
        print(f"{'='*50}")
        
        resources_before = self.measure_resources()
        start_time = time.time()
        
        # Dividir dados em chunks
        chunk_size = len(data) // num_chunks
        chunks = []
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < num_chunks - 1 else len(data)
            chunks.append((i, data[start_idx:end_idx]))
        
        # Processar sequencialmente
        results = []
        for chunk in chunks:
            result = self.process_chunk(chunk)
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        resources_after = self.measure_resources()
        memory_diff = resources_after['memory_mb'] - resources_before['memory_mb']
        
        print(f"📊 Chunks processados: {len(results)}")
        print(f"⏱️ Tempo total: {execution_time:.4f} segundos")
        print(f"🔋 Memória usada: {memory_diff:+.1f} MB")
        
        return {
            'method': 'sequential',
            'execution_time': execution_time,
            'memory_diff': memory_diff,
            'results': results
        }
    
    def thread_parallel_processing(self, data, num_chunks=4, max_workers=4):
        """
        Processamento paralelo com threads
        """
        print(f"\n{'='*50}")
        print(f"PROCESSAMENTO PARALELO - THREADS ({max_workers} workers)")
        print(f"{'='*50}")
        
        resources_before = self.measure_resources()
        start_time = time.time()
        
        # Dividir dados em chunks
        chunk_size = len(data) // num_chunks
        chunks = []
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < num_chunks - 1 else len(data)
            chunks.append((i, data[start_idx:end_idx]))
        
        # Processar com ThreadPoolExecutor
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_results = executor.map(self.process_chunk, chunks)
            results = list(future_results)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        resources_after = self.measure_resources()
        memory_diff = resources_after['memory_mb'] - resources_before['memory_mb']
        
        print(f"📊 Chunks processados: {len(results)}")
        print(f"⏱️ Tempo total: {execution_time:.4f} segundos")
        print(f"🔋 Memória usada: {memory_diff:+.1f} MB")
        print(f"🧵 Threads utilizadas: {max_workers}")
        
        return {
            'method': 'threads',
            'execution_time': execution_time,
            'memory_diff': memory_diff,
            'workers': max_workers,
            'results': results
        }
    
    def process_parallel_processing(self, data, num_chunks=4, max_workers=4):
        """
        Processamento paralelo com processos
        """
        print(f"\n{'='*50}")
        print(f"PROCESSAMENTO PARALELO - PROCESSOS ({max_workers} workers)")
        print(f"{'='*50}")
        
        resources_before = self.measure_resources()
        start_time = time.time()
        
        # Dividir dados em chunks
        chunk_size = len(data) // num_chunks
        chunks = []
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < num_chunks - 1 else len(data)
            chunks.append((i, data[start_idx:end_idx]))
        
        # Processar com ProcessPoolExecutor
        results = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_results = executor.map(self.process_chunk, chunks)
            results = list(future_results)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        resources_after = self.measure_resources()
        memory_diff = resources_after['memory_mb'] - resources_before['memory_mb']
        
        print(f"📊 Chunks processados: {len(results)}")
        print(f"⏱️ Tempo total: {execution_time:.4f} segundos")
        print(f"🔋 Memória usada: {memory_diff:+.1f} MB")
        print(f"🏭 Processos utilizados: {max_workers}")
        
        return {
            'method': 'processes',
            'execution_time': execution_time,
            'memory_diff': memory_diff,
            'workers': max_workers,
            'results': results
        }
    
    def io_bound_sequential(self, num_tasks=10):
        """
        Tarefas I/O bound sequenciais
        """
        print(f"\n{'='*50}")
        print(f"I/O BOUND - SEQUENCIAL ({num_tasks} tarefas)")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        results = []
        for i in range(num_tasks):
            result = self.io_bound_task(i)
            results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"📊 Tarefas completadas: {len(results)}")
        print(f"⏱️ Tempo total: {execution_time:.4f} segundos")
        print(f"📈 Tempo médio por tarefa: {execution_time/num_tasks:.4f} segundos")
        
        return {
            'method': 'io_sequential',
            'execution_time': execution_time,
            'num_tasks': num_tasks,
            'avg_time_per_task': execution_time / num_tasks
        }
    
    def io_bound_threads(self, num_tasks=10, max_workers=5):
        """
        Tarefas I/O bound com threads
        """
        print(f"\n{'='*50}")
        print(f"I/O BOUND - THREADS ({num_tasks} tarefas, {max_workers} workers)")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.io_bound_task, i) for i in range(num_tasks)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"📊 Tarefas completadas: {len(results)}")
        print(f"⏱️ Tempo total: {execution_time:.4f} segundos")
        print(f"📈 Tempo médio por tarefa: {execution_time/num_tasks:.4f} segundos")
        print(f"🧵 Threads utilizadas: {max_workers}")
        
        return {
            'method': 'io_threads',
            'execution_time': execution_time,
            'num_tasks': num_tasks,
            'workers': max_workers,
            'avg_time_per_task': execution_time / num_tasks
        }
    
    def run_cpu_bound_comparison(self, data):
        """
        Executa comparação completa de CPU bound
        """
        print(f"\n{'='*60}")
        print("TESTE DE PERFORMANCE - CPU BOUND")
        print(f"Dados: {len(data):,} valores")
        print(f"{'='*60}")
        
        results = {}
        
        # Sequencial
        results['sequential'] = self.sequential_processing(data)
        
        # Threads
        results['threads'] = self.thread_parallel_processing(data, max_workers=4)
        
        # Processos (apenas se suportado)
        try:
            results['processes'] = self.process_parallel_processing(data, max_workers=2)
        except Exception as e:
            print(f"⚠️ Erro com processos paralelos: {e}")
        
        return results
    
    def run_io_bound_comparison(self):
        """
        Executa comparação completa de I/O bound
        """
        print(f"\n{'='*60}")
        print("TESTE DE PERFORMANCE - I/O BOUND")
        print(f"{'='*60}")
        
        results = {}
        
        # Sequencial
        results['io_sequential'] = self.io_bound_sequential(num_tasks=8)
        
        # Threads
        results['io_threads'] = self.io_bound_threads(num_tasks=8, max_workers=4)
        
        return results
    
    def print_comparison_summary(self, cpu_results, io_results):
        """
        Imprime resumo comparativo
        """
        print(f"\n{'='*60}")
        print("RESUMO COMPARATIVO DE PERFORMANCE")
        print(f"{'='*60}")
        
        print(f"\n🏭 CPU BOUND:")
        if cpu_results:
            for method, result in cpu_results.items():
                if result:
                    print(f"   • {method.upper()}: {result['execution_time']:.4f}s")
        
        print(f"\n🌐 I/O BOUND:")
        if io_results:
            for method, result in io_results.items():
                if result:
                    print(f"   • {method.upper()}: {result['execution_time']:.4f}s "
                          f"({result['avg_time_per_task']:.4f}s/tarefa)")
        
        # Calcular speedup
        if cpu_results and 'sequential' in cpu_results and 'threads' in cpu_results:
            if cpu_results['sequential'] and cpu_results['threads']:
                sequential_time = cpu_results['sequential']['execution_time']
                thread_time = cpu_results['threads']['execution_time']
                speedup = sequential_time / thread_time
                print(f"\n🚀 SPEEDUP (Threads vs Sequential): {speedup:.2f}x")

def main():
    """
    Função principal
    """
    print("🚀 INICIANDO TESTE DE PARALELISMO - PYTHON")
    print("="*60)
    
    processor = ParallelProcessor()
    
    # Carregar dados do CSV para usar nos testes
    csv_path = '../data/large_dataset.csv'
    if os.path.exists(csv_path):
        print(f"📄 Carregando dados de: {csv_path}")
        df = pd.read_csv(csv_path)
        data = df['value'].tolist()
        print(f"📊 Dados carregados: {len(data):,} valores")
    else:
        print("⚠️ Arquivo CSV não encontrado, gerando dados sintéticos...")
        data = list(range(1, 10001))  # Dados de 1 a 10000
    
    # Executar testes
    cpu_results = processor.run_cpu_bound_comparison(data)
    io_results = processor.run_io_bound_comparison()
    
    # Mostrar resumo
    processor.print_comparison_summary(cpu_results, io_results)
    
    print(f"\n✅ TESTES DE PARALELISMO CONCLUÍDOS!")

if __name__ == "__main__":
    main()
