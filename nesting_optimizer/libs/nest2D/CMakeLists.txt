cmake_minimum_required(VERSION 3.15)

project(nest2D LANGUAGES CXX)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Boost and its components
find_package(Boost CONFIG REQUIRED)

if (NOT Boost_FOUND)

    message(STATUS "This project requires the Boost library, and will not be compiled.")

    return()

endif ()

add_subdirectory(lib/pybind11)
add_subdirectory(lib/libnest2d)


set(NEST2D_SOURCES
        src/main.cpp

        # Configs

        #    Selectors
        src/configs/selectors/djd_config.cpp

        #    Placers
        src/configs/placers/bottom_left_config.cpp
        src/configs/placers/nfp_config.cpp

        #    Main Config
        src/configs/config.cpp

        # Geometries

        src/geometries/point.cpp
        src/geometries/item.cpp
        src/geometries/box.cpp

        # Nester

        src/nester/nester.cpp
        src/nester/result.cpp

        # Bindings

        #   Geometries
        src/bindings/geometries/bind_point.cpp
        src/bindings/geometries/bind_item.cpp
        src/bindings/geometries/bind_box.cpp

        #   Nester
        src/bindings/nester/bind_nester.cpp
        src/bindings/nester/bind_result.cpp

        #   Configs

        #       Main Config
        src/bindings/configs/bind_config.cpp

        #       Selectors
        src/bindings/configs/selectors/bind_djd_config.cpp

        #       Placers
        src/bindings/configs/placers/bind_bottom_left_config.cpp
        src/bindings/configs/placers/bind_nfp_config.cpp
)

pybind11_add_module(nest2D MODULE ${NEST2D_SOURCES})
target_include_directories(nest2D PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include/configs/placers
        ${CMAKE_CURRENT_SOURCE_DIR}/include/configs/selectors
        ${CMAKE_CURRENT_SOURCE_DIR}/include/configs

        ${CMAKE_CURRENT_SOURCE_DIR}/include/geometries

        ${CMAKE_CURRENT_SOURCE_DIR}/include/nester

        ${CMAKE_CURRENT_SOURCE_DIR}/include/utils
)

target_link_libraries(nest2D PUBLIC libnest2d)
