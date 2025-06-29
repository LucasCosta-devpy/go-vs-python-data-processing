package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"math/rand"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

// BenchmarkSuite gerencia testes completos de performance
type BenchmarkSuite struct {
	results    map[string]interface{}
	systemInfo SystemInfo
}

// SystemInfo contém informações do sistema
type SystemInfo struct {
	CPUCount        int    `json:"cpu_count"`
	CPUCountLogical int    `json:"cpu_count_logical"`
	MemoryTotalMB   uint64 `json:"memory_total_mb"`
	GOVersion       string `json:"go_version"`
	Timestamp       string `json:"timestamp"`
}

// DatasetInfo informações sobre dataset
type DatasetInfo struct {
	Name     string  `json:"name"`
	Rows     int     `json:"rows"`
	Filename string  `json:"filename"`
	FilePath string  `json:"filepath"`
	SizeMB   float64 `json:"size_mb"`
}

// BenchmarkResult resultado de um benchmark
type BenchmarkResult struct {
	DatasetInfo    DatasetInfo `json:"dataset_info"`
	ExecutionTime  float64     `json:"execution_time"`
	RowsPerSecond  float64     `json:"rows_per_second"`
	MemoryDiffMB   float64     `json:"memory_diff_mb"`
	Method         string      `json:"method"`
	AdditionalInfo interface{} `json:"additional_info,omitempty"`
}

// NewBenchmarkSuite cria nova instância
func NewBenchmarkSuite() *BenchmarkSuite {
	return &BenchmarkSuite{
		results:    make(map[string]interface{}),
		systemInfo: getSystemInfo(),
	}
}

// getSystemInfo coleta informações do sistema
func getSystemInfo() SystemInfo {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	return SystemInfo{
		CPUCount:        runtime.NumCPU(),
		CPUCountLogical: runtime.GOMAXPROCS(0),
		MemoryTotalMB:   m.Sys / (1024 * 1024),
		GOVersion:       runtime.Version(),
		Timestamp:       time.Now().Format(time.RFC3339),
	}
}

// GetMemoryStats obtém estatísticas de memória
func (bs *BenchmarkSuite) GetMemoryStats() float64 {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	return float64(m.Alloc) / 1024 / 1024
}

// GenerateTestDatasets gera datasets de diferentes tamanhos
func (bs *BenchmarkSuite) GenerateTestDatasets() []DatasetInfo {
	datasets := []DatasetInfo{
		{Name: "small", Rows: 1000, Filename: "dataset_1k_go.csv"},
		{Name: "medium", Rows: 10000, Filename: "dataset_10k_go.csv"},
		{Name: "large", Rows: 100000, Filename: "dataset_100k_go.csv"},
		{Name: "xlarge", Rows: 500000, Filename: "dataset_500k_go.csv"},
	}

	fmt.Printf("🔄 GERANDO DATASETS DE TESTE...\n")
	fmt.Printf("%s\n", strings.Repeat("=", 50))

	for i := range datasets {
		dataset := &datasets[i]
		fmt.Printf("📊 Gerando %s: %d linhas...\n", dataset.Name, dataset.Rows)

		filePath, err := bs.generateDataset(dataset.Rows, dataset.Filename)
		if err != nil {
			fmt.Printf("❌ Erro ao gerar %s: %v\n", dataset.Name, err)
			continue
		}

		dataset.FilePath = filePath

		// Verificar tamanho do arquivo
		fileInfo, err := os.Stat(filePath)
		if err != nil {
			fmt.Printf("❌ Erro ao verificar tamanho: %v\n", err)
			continue
		}

		dataset.SizeMB = float64(fileInfo.Size()) / (1024 * 1024)
		fmt.Printf("   ✅ Gerado: %d bytes (%.2f MB)\n", fileInfo.Size(), dataset.SizeMB)
	}

	return datasets
}

// generateDataset gera um dataset CSV
func (bs *BenchmarkSuite) generateDataset(numRows int, filename string) (string, error) {
	dataDir := "../data"
	if err := os.MkdirAll(dataDir, 0755); err != nil {
		return "", fmt.Errorf("erro ao criar diretório: %v", err)
	}

	filePath := filepath.Join(dataDir, filename)

	file, err := os.Create(filePath)
	if err != nil {
		return "", fmt.Errorf("erro ao criar arquivo: %v", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	if err := writer.Write([]string{"id", "value"}); err != nil {
		return "", fmt.Errorf("erro ao escrever cabeçalho: %v", err)
	}

	rand.Seed(time.Now().UnixNano())
	for i := 1; i <= numRows; i++ {
		value := rand.Intn(4950) + 50
		record := []string{
			fmt.Sprintf("%d", i),
			fmt.Sprintf("%d", value),
		}

		if err := writer.Write(record); err != nil {
			return "", fmt.Errorf("erro ao escrever linha %d: %v", i, err)
		}
	}

	return filePath, nil
}

// BenchmarkCSVReading testa leitura de CSV
func (bs *BenchmarkSuite) BenchmarkCSVReading(datasets []DatasetInfo) map[string]BenchmarkResult {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("BENCHMARK: LEITURA DE CSV\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	results := make(map[string]BenchmarkResult)

	for _, dataset := range datasets {
		fmt.Printf("\n🎯 Testando %s (%d linhas)\n", dataset.Name, dataset.Rows)

		if _, err := os.Stat(dataset.FilePath); err != nil {
			fmt.Printf("❌ Arquivo não encontrado: %s\n", dataset.FilePath)
			continue
		}

		memoryBefore := bs.GetMemoryStats()
		startTime := time.Now()

		// Ler CSV
		data, err := bs.readCSV(dataset.FilePath)
		if err != nil {
			fmt.Printf("❌ Erro ao ler CSV: %v\n", err)
			continue
		}

		executionTime := time.Since(startTime).Seconds()
		memoryAfter := bs.GetMemoryStats()
		memoryDiff := memoryAfter - memoryBefore

		// Evitar +Inf no JSON
		var rowsPerSecond float64
		if executionTime > 0 {
			rowsPerSecond = float64(len(data)) / executionTime
		} else {
			rowsPerSecond = float64(len(data)) / 0.0001 // Usar valor muito pequeno
		}

		fmt.Printf("   ⏱️ Tempo de leitura: %.4fs\n", executionTime)
		fmt.Printf("   🚀 Velocidade: %.0f linhas/s\n", rowsPerSecond)
		fmt.Printf("   🔋 Memória usada: %+.1f MB\n", memoryDiff)

		key := fmt.Sprintf("csv_reading_%s", dataset.Name)
		results[key] = BenchmarkResult{
			DatasetInfo:   dataset,
			ExecutionTime: executionTime,
			RowsPerSecond: rowsPerSecond,
			MemoryDiffMB:  memoryDiff,
			Method:        "go_encoding_csv",
		}
	}

	return results
}

// readCSV lê arquivo CSV e retorna slice de valores
func (bs *BenchmarkSuite) readCSV(filePath string) ([]int, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	reader := csv.NewReader(file)

	// Ler cabeçalho
	_, err = reader.Read()
	if err != nil {
		return nil, err
	}

	var data []int
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}

		value, err := strconv.Atoi(record[1])
		if err != nil {
			return nil, err
		}

		data = append(data, value)
	}

	return data, nil
}

// BenchmarkCalculations testa cálculos estatísticos
func (bs *BenchmarkSuite) BenchmarkCalculations(datasets []DatasetInfo) map[string]BenchmarkResult {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("BENCHMARK: CÁLCULOS ESTATÍSTICOS\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	results := make(map[string]BenchmarkResult)

	for _, dataset := range datasets {
		if _, err := os.Stat(dataset.FilePath); err != nil {
			continue
		}

		fmt.Printf("\n🧮 Calculando %s (%d linhas)\n", dataset.Name, dataset.Rows)

		// Carregar dados
		startLoad := time.Now()
		data, err := bs.readCSV(dataset.FilePath)
		if err != nil {
			fmt.Printf("❌ Erro ao carregar dados: %v\n", err)
			continue
		}
		loadTime := time.Since(startLoad).Seconds()

		// Medir recursos antes
		memoryBefore := bs.GetMemoryStats()

		// Executar cálculos
		startCalc := time.Now()
		calculations := bs.calculateStatistics(data)
		calcTime := time.Since(startCalc).Seconds()

		// Medir recursos depois
		memoryAfter := bs.GetMemoryStats()
		memoryDiff := memoryAfter - memoryBefore

		// Evitar +Inf no JSON
		var rowsPerSecond float64
		if calcTime > 0 {
			rowsPerSecond = float64(len(data)) / calcTime
		} else {
			rowsPerSecond = float64(len(data)) / 0.0001 // Usar valor muito pequeno
		}

		fmt.Printf("   ⏱️ Tempo de cálculo: %.4fs\n", calcTime)
		fmt.Printf("   🔋 Memória usada: %+.1f MB\n", memoryDiff)
		fmt.Printf("   📊 Resultados: %d métricas calculadas\n", len(calculations))

		key := fmt.Sprintf("calculations_%s", dataset.Name)
		results[key] = BenchmarkResult{
			DatasetInfo:   dataset,
			ExecutionTime: calcTime,
			RowsPerSecond: rowsPerSecond,
			MemoryDiffMB:  memoryDiff,
			Method:        "go_native",
			AdditionalInfo: map[string]interface{}{
				"load_time":    loadTime,
				"calculations": calculations,
			},
		}
	}

	return results
}

// calculateStatistics calcula estatísticas básicas
func (bs *BenchmarkSuite) calculateStatistics(data []int) map[string]float64 {
	if len(data) == 0 {
		return nil
	}

	// Cálculos básicos
	sum := 0
	min := data[0]
	max := data[0]

	for _, value := range data {
		sum += value
		if value < min {
			min = value
		}
		if value > max {
			max = value
		}
	}

	mean := float64(sum) / float64(len(data))

	// Mediana
	sortedData := make([]int, len(data))
	copy(sortedData, data)
	sort.Ints(sortedData)

	var median float64
	n := len(sortedData)
	if n%2 == 0 {
		median = float64(sortedData[n/2-1]+sortedData[n/2]) / 2
	} else {
		median = float64(sortedData[n/2])
	}

	// Desvio padrão
	var variance float64
	for _, value := range data {
		diff := float64(value) - mean
		variance += diff * diff
	}
	variance /= float64(len(data))
	stdDev := variance // Simplificado

	// Quartis
	q1 := float64(sortedData[n/4])
	q3 := float64(sortedData[3*n/4])

	// Valores únicos
	uniqueMap := make(map[int]bool)
	for _, value := range data {
		uniqueMap[value] = true
	}

	return map[string]float64{
		"sum":          float64(sum),
		"mean":         mean,
		"median":       median,
		"std":          stdDev,
		"min":          float64(min),
		"max":          float64(max),
		"quantile_25":  q1,
		"quantile_75":  q3,
		"count":        float64(len(data)),
		"unique_count": float64(len(uniqueMap)),
	}
}

// BenchmarkParallelProcessing testa processamento paralelo
func (bs *BenchmarkSuite) BenchmarkParallelProcessing(datasets []DatasetInfo) map[string]BenchmarkResult {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("BENCHMARK: PROCESSAMENTO PARALELO\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	results := make(map[string]BenchmarkResult)

	// Testar apenas com datasets médio (para não demorar)
	testDatasets := []DatasetInfo{}
	for _, dataset := range datasets {
		if dataset.Name == "medium" {
			testDatasets = append(testDatasets, dataset)
		}
	}

	for _, dataset := range testDatasets {
		if _, err := os.Stat(dataset.FilePath); err != nil {
			continue
		}

		fmt.Printf("\n🔄 Processamento paralelo: %s (%d linhas)\n", dataset.Name, dataset.Rows)

		// Carregar dados
		data, err := bs.readCSV(dataset.FilePath)
		if err != nil {
			fmt.Printf("❌ Erro ao carregar dados: %v\n", err)
			continue
		}

		// Teste sequencial
		seqResult := bs.benchmarkSequentialProcessing(data, dataset)
		if seqResult != nil {
			key := fmt.Sprintf("parallel_sequential_%s", dataset.Name)
			results[key] = *seqResult
		}

		// Teste com goroutines
		gorResult := bs.benchmarkGoroutineProcessing(data, dataset)
		if gorResult != nil {
			key := fmt.Sprintf("parallel_goroutines_%s", dataset.Name)
			results[key] = *gorResult
		}
	}

	return results
}

// benchmarkSequentialProcessing testa processamento sequencial
func (bs *BenchmarkSuite) benchmarkSequentialProcessing(data []int, dataset DatasetInfo) *BenchmarkResult {
	startTime := time.Now()

	// Processamento simples
	processed := make([]int, len(data))
	for i, value := range data {
		processed[i] = value*2 + 1
	}

	executionTime := time.Since(startTime).Seconds()

	fmt.Printf("   ⏱️ Sequencial: %.4fs\n", executionTime)

	// Evitar +Inf no JSON
	var rowsPerSecond float64
	if executionTime > 0 {
		rowsPerSecond = float64(len(data)) / executionTime
	} else {
		rowsPerSecond = float64(len(data)) / 0.0001
	}

	return &BenchmarkResult{
		DatasetInfo:   dataset,
		ExecutionTime: executionTime,
		RowsPerSecond: rowsPerSecond,
		Method:        "sequential",
	}
}

// benchmarkGoroutineProcessing testa processamento com goroutines
func (bs *BenchmarkSuite) benchmarkGoroutineProcessing(data []int, dataset DatasetInfo) *BenchmarkResult {
	startTime := time.Now()

	numWorkers := 4
	chunkSize := len(data) / numWorkers
	var wg sync.WaitGroup

	// Dividir em chunks e processar com goroutines
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)

		go func(workerID int) {
			defer wg.Done()

			start := workerID * chunkSize
			end := start + chunkSize
			if workerID == numWorkers-1 {
				end = len(data)
			}

			// Processar chunk
			for j := start; j < end; j++ {
				data[j] = data[j]*2 + 1
			}
		}(i)
	}

	wg.Wait()
	executionTime := time.Since(startTime).Seconds()

	fmt.Printf("   ⏱️ Goroutines: %.4fs\n", executionTime)

	// Evitar +Inf no JSON
	var rowsPerSecond float64
	if executionTime > 0 {
		rowsPerSecond = float64(len(data)) / executionTime
	} else {
		rowsPerSecond = float64(len(data)) / 0.0001
	}

	return &BenchmarkResult{
		DatasetInfo:   dataset,
		ExecutionTime: executionTime,
		RowsPerSecond: rowsPerSecond,
		Method:        "goroutines",
		AdditionalInfo: map[string]interface{}{
			"workers": numWorkers,
		},
	}
}

// GeneratePerformanceReport gera relatório de performance
func (bs *BenchmarkSuite) GeneratePerformanceReport(allResults map[string]BenchmarkResult) {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("RELATÓRIO DE PERFORMANCE - GO\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	// Informações do sistema
	fmt.Printf("\n🖥️ INFORMAÇÕES DO SISTEMA:\n")
	fmt.Printf("   • CPU Cores: %d\n", bs.systemInfo.CPUCount)
	fmt.Printf("   • Go Version: %s\n", bs.systemInfo.GOVersion)
	fmt.Printf("   • Memória Sistema: %d MB\n", bs.systemInfo.MemoryTotalMB)
	fmt.Printf("   • Data/Hora: %s\n", bs.systemInfo.Timestamp)

	// Resumo de leitura de CSV
	fmt.Printf("\n📊 PERFORMANCE DE LEITURA DE CSV:\n")
	fmt.Printf("%-15s %-10s %-12s %-10s %-20s\n", "Dataset", "Linhas", "Tamanho (MB)", "Tempo (s)", "Velocidade (linhas/s)")
	fmt.Printf("%s\n", strings.Repeat("-", 75))

	csvResults := make(map[string]BenchmarkResult)
	for k, v := range allResults {
		if strings.HasPrefix(k, "csv_reading_") {
			csvResults[k] = v
		}
	}

	for _, result := range csvResults {
		fmt.Printf("%-15s %-10d %-12.2f %-10.4f %-20.0f\n",
			result.DatasetInfo.Name,
			result.DatasetInfo.Rows,
			result.DatasetInfo.SizeMB,
			result.ExecutionTime,
			result.RowsPerSecond)
	}

	// Resumo de cálculos
	fmt.Printf("\n🧮 PERFORMANCE DE CÁLCULOS:\n")
	fmt.Printf("%-15s %-10s %-10s %-20s\n", "Dataset", "Linhas", "Tempo (s)", "Velocidade (linhas/s)")
	fmt.Printf("%s\n", strings.Repeat("-", 60))

	calcResults := make(map[string]BenchmarkResult)
	for k, v := range allResults {
		if strings.HasPrefix(k, "calculations_") {
			calcResults[k] = v
		}
	}

	for _, result := range calcResults {
		fmt.Printf("%-15s %-10d %-10.4f %-20.0f\n",
			result.DatasetInfo.Name,
			result.DatasetInfo.Rows,
			result.ExecutionTime,
			result.RowsPerSecond)
	}
}

// SaveResultsToFile salva resultados em arquivo JSON
func (bs *BenchmarkSuite) SaveResultsToFile(allResults map[string]BenchmarkResult) string {
	// Criar diretório results se não existir
	resultsDir := "../results"
	if err := os.MkdirAll(resultsDir, 0755); err != nil {
		fmt.Printf("❌ Erro ao criar diretório results: %v\n", err)
		return ""
	}

	// Preparar dados para JSON
	outputData := map[string]interface{}{
		"system_info": bs.systemInfo,
		"results":     allResults,
		"summary": map[string]int{
			"total_tests":       len(allResults),
			"csv_reading_tests": len(getResultsByPrefix(allResults, "csv_reading_")),
			"calculation_tests": len(getResultsByPrefix(allResults, "calculations_")),
			"parallel_tests":    len(getResultsByPrefix(allResults, "parallel_")),
		},
	}

	// Salvar arquivo
	timestamp := time.Now().Format("20060102_150405")
	filename := fmt.Sprintf("go_benchmark_results_%s.json", timestamp)
	filePath := filepath.Join(resultsDir, filename)

	file, err := os.Create(filePath)
	if err != nil {
		fmt.Printf("❌ Erro ao criar arquivo: %v\n", err)
		return ""
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(outputData); err != nil {
		fmt.Printf("❌ Erro ao escrever JSON: %v\n", err)
		return ""
	}

	fmt.Printf("\n💾 Resultados salvos em: %s\n", filePath)
	return filePath
}

// getResultsByPrefix retorna resultados que começam com o prefixo
func getResultsByPrefix(results map[string]BenchmarkResult, prefix string) map[string]BenchmarkResult {
	filtered := make(map[string]BenchmarkResult)
	for k, v := range results {
		if strings.HasPrefix(k, prefix) {
			filtered[k] = v
		}
	}
	return filtered
}

// RunFullBenchmark executa benchmark completo
func (bs *BenchmarkSuite) RunFullBenchmark() map[string]BenchmarkResult {
	fmt.Printf("🚀 INICIANDO BENCHMARK SUITE COMPLETO - GO\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	// Gerar datasets
	datasets := bs.GenerateTestDatasets()

	allResults := make(map[string]BenchmarkResult)

	fmt.Printf("\n🔍 EXECUTANDO BENCHMARKS...\n")

	// 1. Leitura de CSV
	csvResults := bs.BenchmarkCSVReading(datasets)
	for k, v := range csvResults {
		allResults[k] = v
	}

	// 2. Cálculos estatísticos
	calcResults := bs.BenchmarkCalculations(datasets)
	for k, v := range calcResults {
		allResults[k] = v
	}

	// 3. Processamento paralelo
	parallelResults := bs.BenchmarkParallelProcessing(datasets)
	for k, v := range parallelResults {
		allResults[k] = v
	}

	// Gerar relatório
	bs.GeneratePerformanceReport(allResults)

	// Salvar resultados
	bs.SaveResultsToFile(allResults)

	fmt.Printf("\n✅ BENCHMARK SUITE CONCLUÍDO!\n")
	fmt.Printf("📊 Total de testes executados: %d\n", len(allResults))

	return allResults
}

func main() {
	suite := NewBenchmarkSuite()
	suite.RunFullBenchmark()
}
