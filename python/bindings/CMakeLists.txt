# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT dect6_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT dect6_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND dect6_python_files
    python_bindings.cc)

GR_PYBIND_MAKE_OOT(dect6 
   ../..
   gr::dect6
   "${dect6_python_files}")

install(TARGETS dect6_python DESTINATION ${GR_PYTHON_DIR}/dect6 COMPONENT pythonapi)
