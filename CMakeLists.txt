cmake_minimum_required(VERSION 2.8)
project(libstddumb)

set(CMAKE_BUILD_TYPE Release)
file(GLOB SOURCES libstddumb/*.c)

add_library(stddumb SHARED ${SOURCES})

install(TARGETS stddumb DESTINATION lib)
