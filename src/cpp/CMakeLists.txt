cmake_minimum_required(VERSION 3.4...3.18)
project(roll_card)

set(pybind11_DIR "D:/Programing/test/TextProbAnalisis/env/Lib/site-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 REQUIRED)
pybind11_add_module(roll_card roll_card.cpp)