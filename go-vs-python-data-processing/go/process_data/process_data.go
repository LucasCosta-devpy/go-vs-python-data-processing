package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"math"
	"math/rand"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"time"
)

// DataRecord representa um registro de dados
type DataRecord struct {
	ID    int
	Value int
}

// DataProcessor gerencia o processamento de dados e medição de performance
type DataProcessor struct {
	results map[string]interface{}
}

// NewDataProcessor cria uma nova instância do processador
func NewDataProcessor() *DataProcessor {
	return &DataProcessor{
		results: make(map[string]interface{}),
	}
}

// MemoryStats obtém estatísticas de memória
func (dp *DataProcessor) GetMemoryStats() (float64, float64) {
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	allocMB := float64(m.Alloc) / 1024 / 1024
	sysMB := float64(m.Sys) / 1024 / 1024

	return allocMB, sysMB
}

// ReadCSVWithTiming lê CSV e mede performance
func (dp *DataProcessor) ReadCSVWithTiming(filepath string) ([]DataRecord, error) {
	fmt.Printf("\n%s\n", strings.Repeat("=", 50))
	fmt.Printf("LENDO CSV: %s\n", filepath)
	fmt.Printf("Método: Go encoding/csv\n")
	fmt.Printf("%s\n", strings.Repeat("=", 50))

	// Verificar se arquivo existe
	fileInfo, err := os.Stat(filepath)
	if err != nil {
		fmt.Printf("❌ Arquivo não encontrado: %s\n", filepath)
		return nil, err
	}

	fileSize := fileInfo.Size()
	fmt.Printf("📁 Tamanho do arquivo: %d bytes (%.2f MB)\n", fileSize, float64(fileSize)/(1024*1024))

	// Medição de recursos antes
	allocBefore, sysBefore := dp.GetMemoryStats()
	fmt.Printf("🔋 Recursos ANTES - Alloc: %.1f MB | Sys: %.1f MB\n", allocBefore, sysBefore)

	// Medir tempo de leitura
	startTime := time.Now()

	// Abrir arquivo
	file, err := os.Open(filepath)
	if err != nil {
		return nil, fmt.Errorf("erro ao abrir arquivo: %v", err)
	}
	defer file.Close()

	// Criar reader CSV
	reader := csv.NewReader(file)

	// Ler cabeçalho
	headers, err := reader.Read()
	if err != nil {
		return nil, fmt.Errorf("erro ao ler cabeçalho: %v", err)
	}
	_ = headers // Ignorar cabeçalho por enquanto

	// Ler dados
	var records []DataRecord
	lineCount := 0

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("erro ao ler linha %d: %v", lineCount+1, err)
		}

		// Converter dados
		id, err := strconv.Atoi(record[0])
		if err != nil {
			return nil, fmt.Errorf("erro ao converter ID na linha %d: %v", lineCount+1, err)
		}

		value, err := strconv.Atoi(record[1])
		if err != nil {
			return nil, fmt.Errorf("erro ao converter Value na linha %d: %v", lineCount+1, err)
		}

		records = append(records, DataRecord{ID: id, Value: value})
		lineCount++
	}

	executionTime := time.Since(startTime)

	// Medição de recursos depois
	allocAfter, sysAfter := dp.GetMemoryStats()

	// Forçar garbage collection para medição mais precisa
	runtime.GC()

	fmt.Printf("\n📊 DADOS CARREGADOS:\n")
	fmt.Printf("   • Linhas: %d\n", len(records))
	fmt.Printf("   • Colunas: 2 (id, value)\n")

	fmt.Printf("\n⏱️  PERFORMANCE:\n")
	fmt.Printf("   • Tempo de execução: %.4f segundos\n", executionTime.Seconds())
	fmt.Printf("   • Velocidade: %.0f linhas/segundo\n", float64(len(records))/executionTime.Seconds())

	memoryDiff := allocAfter - allocBefore
	fmt.Printf("\n🔋 RECURSOS DEPOIS - Alloc: %.1f MB | Sys: %.1f MB\n", allocAfter, sysAfter)
	fmt.Printf("   • Diferença de memória: %+.1f MB\n", memoryDiff)

	return records, nil
}

// CalculateStatistics calcula estatísticas básicas
func (dp *DataProcessor) CalculateStatistics(records []DataRecord) map[string]float64 {
	if len(records) == 0 {
		fmt.Println("❌ Sem dados para calcular")
		return nil
	}

	fmt.Printf("\n%s\n", strings.Repeat("=", 50))
	fmt.Printf("EXECUTANDO CÁLCULOS BÁSICOS\n")
	fmt.Printf("%s\n", strings.Repeat("=", 50))

	allocBefore, _ := dp.GetMemoryStats()
	startTime := time.Now()

	// Extrair valores para cálculos
	values := make([]int, len(records))
	for i, record := range records {
		values[i] = record.Value
	}

	// Cálculos básicos
	sum := 0
	min := values[0]
	max := values[0]

	for _, value := range values {
		sum += value
		if value < min {
			min = value
		}
		if value > max {
			max = value
		}
	}

	mean := float64(sum) / float64(len(values))

	// Mediana
	sortedValues := make([]int, len(values))
	copy(sortedValues, values)
	sort.Ints(sortedValues)

	var median float64
	n := len(sortedValues)
	if n%2 == 0 {
		median = float64(sortedValues[n/2-1]+sortedValues[n/2]) / 2
	} else {
		median = float64(sortedValues[n/2])
	}

	// Desvio padrão
	var variance float64
	for _, value := range values {
		variance += math.Pow(float64(value)-mean, 2)
	}
	variance /= float64(len(values))
	stdDev := math.Sqrt(variance)

	// Quartis
	q1 := float64(sortedValues[n/4])
	q3 := float64(sortedValues[3*n/4])

	// Valores únicos
	uniqueMap := make(map[int]bool)
	for _, value := range values {
		uniqueMap[value] = true
	}
	uniqueCount := len(uniqueMap)

	calculations := map[string]float64{
		"soma_total":    float64(sum),
		"media":         mean,
		"mediana":       median,
		"min_valor":     float64(min),
		"max_valor":     float64(max),
		"desvio_padrao": stdDev,
		"quartil_25":    q1,
		"quartil_75":    q3,
		"count":         float64(len(values)),
		"unique_count":  float64(uniqueCount),
	}

	executionTime := time.Since(startTime)
	allocAfter, _ := dp.GetMemoryStats()
	memoryDiff := allocAfter - allocBefore

	fmt.Printf("\n📈 RESULTADOS DOS CÁLCULOS:\n")
	for key, value := range calculations {
		if key == "count" || key == "unique_count" {
			fmt.Printf("   • %s: %.0f\n", strings.Title(strings.ReplaceAll(key, "_", " ")), value)
		} else {
			fmt.Printf("   • %s: %.2f\n", strings.Title(strings.ReplaceAll(key, "_", " ")), value)
		}
	}

	fmt.Printf("\n⏱️  PERFORMANCE CÁLCULOS:\n")
	fmt.Printf("   • Tempo: %.4f segundos\n", executionTime.Seconds())
	fmt.Printf("   • Memória extra: %+.1f MB\n", memoryDiff)

	return calculations
}

// CompareReadingMethods compara diferentes métodos (por enquanto só um)
func (dp *DataProcessor) CompareReadingMethods(filepath string) {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("COMPARAÇÃO DE MÉTODOS DE LEITURA\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	records, err := dp.ReadCSVWithTiming(filepath)
	if err != nil {
		fmt.Printf("❌ Erro: %v\n", err)
		return
	}

	if records != nil {
		dp.CalculateStatistics(records)
	}
}

// PrintSummary imprime resumo dos resultados
func (dp *DataProcessor) PrintSummary() {
	fmt.Printf("\n%s\n", strings.Repeat("=", 60))
	fmt.Printf("RESUMO DOS RESULTADOS\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	// Por enquanto, apenas mensagem informativa
	fmt.Printf("Processamento concluído com sucesso!\n")
}

// GenerateDataset gera um CSV com numRows linhas
func GenerateDataset(numRows int, filename string) (string, error) {
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
		record := []string{fmt.Sprintf("%d", i), fmt.Sprintf("%d", value)}
		if err := writer.Write(record); err != nil {
			return "", fmt.Errorf("erro ao escrever linha %d: %v", i, err)
		}
	}

	return filePath, nil
}

func main() {
	fmt.Printf("🚀 INICIANDO TESTE DE PERFORMANCE - GO\n")
	fmt.Printf("%s\n", strings.Repeat("=", 60))

	processor := NewDataProcessor()

	// Caminhos dos arquivos
	largeDatasetPath := "../data/large_dataset_go.csv"
	sampleDatasetPath := "../data/sample_dataset.csv"

	// Verificar se o dataset grande existe
	if _, err := os.Stat(largeDatasetPath); os.IsNotExist(err) {
		fmt.Printf("⚠️  Dataset grande não encontrado: %s\n", largeDatasetPath)
		fmt.Printf("🔄 Gerando dataset...\n")

		if newPath, err := GenerateDataset(10000, "large_dataset_go.csv"); err != nil {
			fmt.Printf("❌ Erro ao gerar dataset: %v\n", err)
			return
		} else {
			largeDatasetPath = newPath
		}
	}

	// Testar com dataset grande
	if _, err := os.Stat(largeDatasetPath); err == nil {
		fmt.Printf("\n🎯 TESTANDO COM DATASET GRANDE\n")
		processor.CompareReadingMethods(largeDatasetPath)
	}

	// Testar com dataset pequeno para comparação
	if _, err := os.Stat(sampleDatasetPath); err == nil {
		fmt.Printf("\n🎯 TESTANDO COM DATASET PEQUENO (comparação)\n")
		processor.CompareReadingMethods(sampleDatasetPath)
	}

	// Mostrar resumo
	processor.PrintSummary()

	fmt.Printf("\n✅ TESTE CONCLUÍDO!\n")
}
