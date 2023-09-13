# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/home/tomas/esp/esp-idf/components/bootloader/subproject"
  "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader"
  "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader-prefix"
  "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader-prefix/tmp"
  "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader-prefix/src/bootloader-stamp"
  "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader-prefix/src"
  "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/tomas/Documents/universidad/octavo_semestre/Sistemas embebidos/tarea-1/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
