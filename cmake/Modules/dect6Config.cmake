if(NOT PKG_CONFIG_FOUND)
    INCLUDE(FindPkgConfig)
endif()
PKG_CHECK_MODULES(PC_DECT6 dect6)

FIND_PATH(
    DECT6_INCLUDE_DIRS
    NAMES dect6/api.h
    HINTS $ENV{DECT6_DIR}/include
        ${PC_DECT6_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    DECT6_LIBRARIES
    NAMES gnuradio-dect6
    HINTS $ENV{DECT6_DIR}/lib
        ${PC_DECT6_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/dect6Target.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(DECT6 DEFAULT_MSG DECT6_LIBRARIES DECT6_INCLUDE_DIRS)
MARK_AS_ADVANCED(DECT6_LIBRARIES DECT6_INCLUDE_DIRS)
