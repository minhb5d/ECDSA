cmake_minimum_required(VERSION 3.16)
project(custom_eddsa_benchmark LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(eddsa_benchmark src/cpp/benchmark.cpp)

if(MSVC)
    target_compile_options(eddsa_benchmark PRIVATE /O2 /W4)
else()
    target_compile_options(eddsa_benchmark PRIVATE -O2 -Wall -Wextra -Wpedantic)
endif()

