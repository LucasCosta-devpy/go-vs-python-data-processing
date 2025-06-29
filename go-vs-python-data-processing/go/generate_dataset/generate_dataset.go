package main

import (
	"encoding/csv"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"time"
)

// GenerateDataset gera um CSV com numRows linhas
func GenerateDataset(numRows int, filename string) (string, error) {
	// Criar diretório data se não existir
	dataDir := "../data"
	if err := os.MkdirAll(dataDir, 0755); err != nil {
		return "", fmt.Errorf("erro ao criar diretório: %v", err)
	}

	filepath := filepath.Join(dataDir, filename)

	fmt.Printf("Gerando dataset com %d linhas...\n", numRows)

	// Criar arquivo
	file, err := os.Create(filepath)
	if err != nil {
		return "", fmt.Errorf("erro ao criar arquivo: %v", err)
	}
	defer file.Close()

	// Criar writer CSV
	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Escrever cabeçalho
	if err := writer.Write([]string{"id", "value"}); err != nil {
		return "", fmt.Errorf("erro ao escrever cabeçalho: %v", err)
	}

	// Seed para números aleatórios
	rand.Seed(time.Now().UnixNano())

	// Gerar dados
	for i := 1; i <= numRows; i++ {
		value := rand.Intn(4950) + 50 // Valores entre 50 e 5000
		record := []string{
			fmt.Sprintf("%d", i),
			fmt.Sprintf("%d", value),
		}

		if err := writer.Write(record); err != nil {
			return "", fmt.Errorf("erro ao escrever linha %d: %v", i, err)
		}
	}

	// Verificar tamanho do arquivo
	fileInfo, err := os.Stat(filepath)
	if err != nil {
		return "", fmt.Errorf("erro ao obter info do arquivo: %v", err)
	}

	fileSize := fileInfo.Size()
	fmt.Printf("Dataset gerado com sucesso!\n")
	fmt.Printf("Localização: %s\n", filepath)
	fmt.Printf("Tamanho: %d bytes (%.2f MB)\n", fileSize, float64(fileSize)/(1024*1024))
	fmt.Printf("Linhas: %d (+ 1 cabeçalho)\n", numRows)

	return filepath, nil
}

func main() {
	// Gerar dataset padrão de 10k linhas
	if _, err := GenerateDataset(10000, "large_dataset_go.csv"); err != nil {
		fmt.Printf("Erro: %v\n", err)
		os.Exit(1)
	}
}
