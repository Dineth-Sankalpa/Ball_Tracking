# Findlibfreenect.cmake

# 1. Find the exact path of the header file itself
find_path(FREENECT_HEADER_PATH
  NAMES libfreenect.h
  PATH_SUFFIXES libfreenect
  PATHS /usr/include /usr/local/include
)

# 2. Extract the parent directory so the compiler can resolve #include "libfreenect/libfreenect.h"
if(FREENECT_HEADER_PATH)
  get_filename_component(libfreenect_INCLUDE_DIR ${FREENECT_HEADER_PATH} DIRECTORY)
endif()

# 3. Find the compiled C++ library
find_library(libfreenect_LIBRARY
  NAMES freenect
  PATHS /usr/lib /usr/local/lib /usr/lib/aarch64-linux-gnu /usr/lib/x86_64-linux-gnu
)

# 4. Standard validation
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(libfreenect
  DEFAULT_MSG
  libfreenect_LIBRARY libfreenect_INCLUDE_DIR
)

# 5. Set the final variables used by kinect_ros2
if(libfreenect_FOUND)
  set(libfreenect_INCLUDE_DIRS ${libfreenect_INCLUDE_DIR} ${FREENECT_HEADER_PATH})
  set(libfreenect_LIBRARIES ${libfreenect_LIBRARY})
endif()
