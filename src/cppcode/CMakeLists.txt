add_library(pyslibtesseract SHARED main.cpp)
target_link_libraries (pyslibtesseract  lept tesseract)
