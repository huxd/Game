project(python)

cmake_minimum_required(VERSION 3.4.1)

include_directories("D:/Python27/include")
link_directories("D:/Python27/libs")

add_library(spam SHARED spam.cpp)

target_link_libraries(spam python27)