cmake_minimum_required(VERSION 3.24)

# Compila para la GPU de la máquina que compila.
if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
  set(CMAKE_CUDA_ARCHITECTURES native)
endif()

project(convolucion_cuda LANGUAGES CXX CUDA)

# Release por defecto: sin optimizar, la CPU sale mucho más lenta y la comparación no es justa.
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)  # para que VS Code encuentre los .h

file(GLOB fuentes src/*/*.cpp src/*/*.cu)
add_executable(convolucion ${fuentes})
target_include_directories(convolucion PRIVATE common src/modelo src/vista src/controlador)
