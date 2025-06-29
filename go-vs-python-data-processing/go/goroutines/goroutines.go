package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"math/rand"
	"os"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"
)

// ParallelProcessor gerencia processamento paralelo com goroutines
type ParallelProcessor struct {
	results map[string]interface{}
}

// NewParallelProcessor cria uma nova instância
func NewParallelProcessor() *ParallelProcessor {
	return &ParallelProcessor{
		results: make(map[string]interface{}),
	}
}

// GetMemoryStats obtém estatísticas de memória
func (pp *ParallelProcessor) GetMemoryStats() (float64, float64) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	allocMB := float64(m.Alloc) / 1024 / 1024
	sysMB := float64(m.Sys) / 1024 / 1024

	return allocMB, sysMB
}

// ProcessChunk processa um chunk de dados (simulação CPU-intensiva)
func (pp *ParallelProcessor) ProcessChunk(chunkID int, data []int, results chan<- ChunkResult) {
	// Simular processamento CPU-intensivo
	processed := make([]int, len(data))
	originalSum := 0
	processedSum := 0

	for i, value := range data {
		// Operações matemáticas
		processedValue := (value*value + value*3 + 17) % 1000
		processed[i] = processedValue

		originalSum += value
		processedSum += processedValue
	}

	// Enviar resultado para o canal
	results <- ChunkResult{
		ChunkID:      chunkID,
		OriginalSum:  originalSum,
		ProcessedSum: processedSum,
		Count:        len(data),
	}
}

// ChunkResult representa o resultado de um chunk processado
type ChunkResult struct {
	ChunkID      int
	OriginalSum  int
	ProcessedSum int
	Count        int
}

// IOTask simula tarefa I/O bound
func (pp *ParallelProcessor) IOTask(taskID int, results chan<- IOResult) {
	// Simular delay de I/O
	delay := time.Duration(rand.Intn(200)+100) * time.Millisecond
	time.Sleep(delay)

	results <- IOResult{
		TaskID: taskID,
		Delay:  delay,
		Result: fmt.Sprintf("Task %d completed", taskID),
	}
}

// IOResult representa resultado de tarefa I/O
type IOResult struct {
	TaskID int
	Delay  time.Duration
	Result string
}

// SequentialProcessing processa dados sequencialmente
func (pp *ParallelProcessor) SequentialProcessing(data []int, numChunks int) map[string]interface{} {
	fmt.Printf("\n%s\n", strings.Repeat("=", 50))
	fmt.Printf("PROCESSAMENTO SEQUENCIAL\n")
	fmt.Printf("%s\n", strings.Repeat("=", 50))

	allocBefore, _ := pp.GetMemoryStats()
	startTime := time.Now()

	// Dividir dados em chunks
	chunkSize := len(data) / numChunks
	var results []ChunkResult

	for i := 0; i < numChunks; i++ {
		startIdx := i * chunkSize
		endIdx := startIdx + chunkSize
		if i == numChunks-1 {
			endIdx = len(data)
		}

		chunk := data[startIdx:endIdx]

		// Processar chunk sequencialmente
		processed := make([]int, len(chunk))
		originalSum := 0
		processedSum := 0

		for j, value := range chunk {
			processedValue := (value*value + value*3 + 17) % 1000
			processed[j] = processedValue

			originalSum += value
			processedSum += processedValue
		}

		results = append(results, ChunkResult{
			ChunkID:      i,
			OriginalSum:  originalSum,
			ProcessedSum: processedSum,
			Count:        len(chunk),
		})
	}

	executionTime := time.Since(startTime)
	allocAfter, _ := pp.GetMemoryStats()
	memoryDiff := allocAfter - allocBefore

	fmt.Printf("📊 Chunks processados: %d\n", len(results))
	fmt.Printf("⏱️ Tempo total: %.4f segundos\n", executionTime.Seconds())
	fmt.Printf("🔋 Memória usada: %+.1f MB\n", memoryDiff)

	return map[string]interface{}{
		"method":         "sequential",
		"execution_time": executionTime.Seconds(),
		"memory_diff":    memoryDiff,
		"results":        results,
	}
}

// GoroutineParallelProcessing processa dados com goroutines
func (pp *ParallelProcessor) GoroutineParallelProcessing(data []int, numChunks int, maxWorkers int) map[string]interface{} {
	fmt.Printf("\n%s\n", strings.Repeat("=", 50))
	fmt.Printf("PROCESSAMENTO PARALELO - GOROUTINES (%d workers)\n", maxWorkers)
	fmt.Printf("%s\n", strings.Repeat("=", 50))

	allocBefore, _ := pp.GetMemoryStats()
	startTime := time.Now()

	// Canal para resultados
	resultsChan := make(chan ChunkResult, numChunks)

	// WaitGroup para sincronização
	var wg sync.WaitGroup

	// Dividir dados em chunks
	chunkSize := len(data) / numChunks

	// Lançar goroutines
	for i := 0; i < numChunks; i++ {
		wg.Add(1)

		go func(chunkID int) {
			defer wg.Done()

			startIdx := chunkID * chunkSize
			endIdx := startIdx + chunkSize
			if chunkID == numChunks-1 {
				endIdx = len(data)
			}

			chunk := data[startIdx:endIdx]
			pp.ProcessChunk(chunkID, chunk, resultsChan)
		}(i)
	}

	// Goroutine para fechar canal após processamento
	go func() {
		wg.Wait()
		close(resultsChan)
	}()

	// Coletar resultados
	var results []ChunkResult
	for result := range resultsChan {
		results = append(results, result)
	}

	executionTime := time.Since(startTime)
	allocAfter, _ := pp.GetMemoryStats()
	memoryDiff := allocAfter - allocBefore

	fmt.Printf("📊 Chunks processados: %d\n", len(results))
	fmt.Printf("⏱️ Tempo total: %.4f segundos\n", executionTime.Seconds())
	fmt.Printf("🔋 Memória usada: %+.1f MB\n", memoryDiff)
	fmt.Printf("🚀 Goroutines utilizadas: %d\n", maxWorkers)

	return map[string]interface{}{
		"method":         "goroutines",
		"execution_time": executionTime.Seconds(),
		"memory_diff":    memoryDiff,
		"workers":        maxWorkers,
		"results":        results,
	}
}

// IOBoundSequential executa tarefas I/O sequencialmente
func (pp *ParallelProcessor) IOBoundSequential(numTasks int) map[string]interface{} {
	fmt.Printf("\n%s\n", strings.Repeat("=", 50))
	fmt.Printf("I/O BOUND - SEQUENCIAL (%d tarefas)\n", numTasks)
	fmt.Printf("%s\n", strings.Repeat("=", 50))

	startTime := time.Now()

	var results []IOResult
	for i := 0; i < numTasks; i++ {
		// Simular delay I/O
		delay := time.Duration(rand.Intn(200)+100) * time.Millisecond
		time.Sleep(delay)

		results = append(results, IOResult{
			TaskID: i,
			Delay:  delay,
			Result: fmt.Sprintf("Task %d completed", i),
		})
	}

	executionTime := time.Since(startTime)

	fmt.Printf("📊 Tarefas completadas: %d\n", len(results))
	fmt.Printf("⏱️ Tempo total: %.4f segundos\n", executionTime.Seconds())
	fmt.Printf("📈 Tempo médio por tarefa: %.4f segundos\n", executionTime.Seconds()/float64(numTasks))

	return map[string]interface{}{
		"method":            "io_sequential",
		"execution_time":    executionTime.Seconds(),
		"num_tasks":         numTasks,
		"avg_time_per_task": executionTime.Seconds() / float64(numTasks),
	}
}

// IOBoundGoroutines executa tarefas I/O com goroutines
func (pp *ParallelProcessor) IOBoundGoroutines(numTasks int, maxWorkers int) map[string]interface{} {
	fmt.Printf("\n%s\n", strings.Repeat("=", 50))
	fmt.Printf("I/O BOUND - GOROUTINES (%d tarefas, %d workers)\n", numTasks, maxWorkers)
	fmt.Printf("%s\n", strings.Repeat("=", 50))

	startTime := time.Now()

	// Canal para resultados
	resultsChan := make(chan IOResult, numTasks)

	// WaitGroup para sincronização
	var wg sync.WaitGroup

	// Lançar goroutines
	for i := 0; i < numTasks; i++ {
		wg.Add(1)

		go func(taskID int) {
			defer wg.Done()
			pp.IOTask(taskID, resultsChan)
		}(i)
	}

	// Goroutine para fechar canal
	go func() {
		wg.Wait()
		close(resultsChan)
	}()

	// Coletar resultados
	var results []IOResult
	for result := range resultsChan {
		results = append(results, result)
	}

	executionTime := time.Since(startTime)

	fmt.Printf("📊 Tarefas completadas: %d\n", len(results))
	fmt.Printf("⏱️ Tempo total: %.4f segundos\n", executionTime.Seconds())
	fmt.Printf("📈 Tempo médio por tarefa: %.4f segundos\n", executionTime.Seconds()/float64(numTasks))
	fmt.Printf("🚀 Goroutines utilizadas: %d\n", maxWorkers)

	return map[string]interface{}{
		"method":            "io_goroutines",
		"execution_time":    executionTime.Seconds(),
		"num_tasks":         numTasks,
		"workers":           maxWorkers,
		"avg_time_per_task": executionTime.Seconds() / float64(numTasks),
	}
}

// RunCPUBoundComparison executa comparação completa de CPU bound
func (pp *ParallelProcessor) RunCPUBoundComparison(data []int) map[string]map[string]interface{} {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("TESTE DE PERFORMANCE - CPU BOUND\n")
	fmt.Printf("Dados: %d valores\n", len(data))
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	results := make(map[string]map[string]interface{})

	// Sequencial
	results["sequential"] = pp.SequentialProcessing(data, 4)

	// Goroutines
	results["goroutines"] = pp.GoroutineParallelProcessing(data, 4, 4)

	return results
}

// RunIOBoundComparison executa comparação completa de I/O bound
func (pp *ParallelProcessor) RunIOBoundComparison() map[string]map[string]interface{} {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("TESTE DE PERFORMANCE - I/O BOUND\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	results := make(map[string]map[string]interface{})

	// Sequencial
	results["io_sequential"] = pp.IOBoundSequential(8)

	// Goroutines
	results["io_goroutines"] = pp.IOBoundGoroutines(8, 4)

	return results
}

// PrintComparisonSummary imprime resumo comparativo
func (pp *ParallelProcessor) PrintComparisonSummary(cpuResults, ioResults map[string]map[string]interface{}) {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("RESUMO COMPARATIVO DE PERFORMANCE\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	fmt.Printf("\n🏭 CPU BOUND:\n")
	if cpuResults != nil {
		for method, result := range cpuResults {
			if execTime, ok := result["execution_time"].(float64); ok {
				fmt.Printf("   • %s: %.4fs\n", strings.ToUpper(method), execTime)
			}
		}
	}

	fmt.Printf("\n🌐 I/O BOUND:\n")
	if ioResults != nil {
		for method, result := range ioResults {
			if execTime, ok := result["execution_time"].(float64); ok {
				if avgTime, ok := result["avg_time_per_task"].(float64); ok {
					fmt.Printf("   • %s: %.4fs (%.4fs/tarefa)\n",
						strings.ToUpper(method), execTime, avgTime)
				}
			}
		}
	}

	// Calcular speedup
	if cpuResults != nil {
		if seqResult, ok := cpuResults["sequential"]; ok {
			if gorResult, ok := cpuResults["goroutines"]; ok {
				if seqTime, ok := seqResult["execution_time"].(float64); ok {
					if gorTime, ok := gorResult["execution_time"].(float64); ok {
						speedup := seqTime / gorTime
						fmt.Printf("\n🚀 SPEEDUP (Goroutines vs Sequential): %.2fx\n", speedup)
					}
				}
			}
		}
	}
}

// LoadDataFromCSV carrega dados de um arquivo CSV
func (pp *ParallelProcessor) LoadDataFromCSV(filepath string) ([]int, error) {
	file, err := os.Open(filepath)
	if err != nil {
		return nil, fmt.Errorf("erro ao abrir arquivo: %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)

	// Ler cabeçalho
	_, err = reader.Read()
	if err != nil {
		return nil, fmt.Errorf("erro ao ler cabeçalho: %v", err)
	}

	var data []int
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("erro ao ler linha: %v", err)
		}

		value, err := strconv.Atoi(record[1])
		if err != nil {
			return nil, fmt.Errorf("erro ao converter valor: %v", err)
		}

		data = append(data, value)
	}

	return data, nil
}

func main() {
	fmt.Printf("🚀 INICIANDO TESTE DE PARALELISMO - GO\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	processor := NewParallelProcessor()

	// Seed para números aleatórios
	rand.Seed(time.Now().UnixNano())

	// Carregar dados do CSV
	csvPath := "../data/large_dataset_go.csv"
	var data []int

	if _, err := os.Stat(csvPath); err == nil {
		fmt.Printf("📄 Carregando dados de: %s\n", csvPath)
		if loadedData, err := processor.LoadDataFromCSV(csvPath); err != nil {
			fmt.Printf("⚠️ Erro ao carregar CSV, usando dados sintéticos: %v\n", err)
			// Dados sintéticos
			data = make([]int, 10000)
			for i := range data {
				data[i] = rand.Intn(4950) + 50
			}
		} else {
			data = loadedData
		}
		fmt.Printf("📊 Dados carregados: %d valores\n", len(data))
	} else {
		fmt.Printf("⚠️ Arquivo CSV não encontrado, gerando dados sintéticos...\n")
		data = make([]int, 10000)
		for i := range data {
			data[i] = rand.Intn(4950) + 50
		}
	}

	// Executar testes
	cpuResults := processor.RunCPUBoundComparison(data)
	ioResults := processor.RunIOBoundComparison()

	// Mostrar resumo
	processor.PrintComparisonSummary(cpuResults, ioResults)

	fmt.Printf("\n✅ TESTES DE PARALELISMO CONCLUÍDOS!\n")
}
