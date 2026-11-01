CC = gcc
CFLAGS = -O2 -Wall -std=c99 -Iinclude
NVCC = nvcc
NVFLAGS = -O2 -Iinclude

OBJETOS = bin/imagen.o bin/mascaras.o bin/conv_cpu.o

.PHONY: all cpu test clean

all: bin/filtrar_cpu bin/test_manual bin/filtrar_gpu bin/test_gpu bin/benchmark

cpu: bin/filtrar_cpu bin/test_manual

test: bin/test_manual bin/test_gpu
	./bin/test_manual
	./bin/test_gpu

bin:
	mkdir -p bin

bin/imagen.o: src/imagen.c include/imagen.h | bin
	$(CC) $(CFLAGS) -c $< -o $@

bin/mascaras.o: src/mascaras.c include/mascaras.h | bin
	$(CC) $(CFLAGS) -c $< -o $@

bin/conv_cpu.o: src/conv_cpu.c include/conv_cpu.h include/imagen.h include/mascaras.h | bin
	$(CC) $(CFLAGS) -c $< -o $@

bin/filtrar_cpu: src/filtrar_cpu.c $(OBJETOS) include/comun.h | bin
	$(CC) $(CFLAGS) $< $(OBJETOS) -o $@ -lm

bin/test_manual: tests/test_manual.c $(OBJETOS) | bin
	$(CC) $(CFLAGS) $< $(OBJETOS) -o $@ -lm

bin/conv_gpu.o: src/conv_gpu.cu include/conv_gpu.h | bin
	$(NVCC) $(NVFLAGS) -c $< -o $@

bin/test_gpu.o: tests/test_gpu.cu include/conv_gpu.h | bin
	$(NVCC) $(NVFLAGS) -c $< -o $@

bin/filtrar_gpu.o: src/filtrar_gpu.cu include/conv_gpu.h | bin
	$(NVCC) $(NVFLAGS) -c $< -o $@

bin/benchmark.o: experimentos/benchmark.cu include/conv_gpu.h | bin
	$(NVCC) $(NVFLAGS) -c $< -o $@

bin/filtrar_gpu: bin/filtrar_gpu.o bin/conv_gpu.o $(OBJETOS)
	$(NVCC) $^ -o $@

bin/test_gpu: bin/test_gpu.o bin/conv_gpu.o $(OBJETOS)
	$(NVCC) $^ -o $@

bin/benchmark: bin/benchmark.o bin/conv_gpu.o $(OBJETOS)
	$(NVCC) $^ -o $@

clean:
	rm -f bin/*.o bin/filtrar_cpu bin/test_manual bin/filtrar_gpu bin/test_gpu bin/benchmark
