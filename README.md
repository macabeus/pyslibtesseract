# pyslibtesseract
Integration of Tesseract for Python using a shared library

## To install

From PyPI

    sudo pip3 install pyslibtesseract
    
From Github

    sudo apt-get install libtesseract-dev
    sudo apt-get install libleptonica-dev
    git clone https://github.com/brunomacabeusbr/pyslibtesseract.git
    cd pyslibtesseract
    cd src/cppcode/ && cmake . && make && cd ../.. && sudo python3 setup.py install

## To use
### Start

You must create a object of TesseractConfig:

    config_single_char = TesseractConfig(psm=PageSegMode.PSM_SINGLE_CHAR)
    config_line = TesseractConfig(psm=PageSegMode.PSM_SINGLE_LINE)
    config_line_portuguese_brazilian = TesseractConfig(psm=PageSegMode.PSM_SINGLE_LINE, lang='pt-br')

Possible PSM (page segmentation mode) are:

    PSM_OSD_ONLY
    PSM_AUTO_OSD
    PSM_AUTO_ONLY
    PSM_AUTO
    PSM_SINGLE_COLUMN
    PSM_SINGLE_BLOCK_VERT_TEX
    PSM_SINGLE_BLOCK
    PSM_SINGLE_LINE
    PSM_SINGLE_WORD
    PSM_CIRCLE_WORD
    PSM_SINGLE_CHAR
    PSM_SPARSE_TEXT
    PSM_SPARSE_TEXT_OSD
    PSM_COUNT

You can set <a href="http://www.sk-spell.sk.cx/tesseract-ocr-parameters-in-302-version">variables of Tesseract</a>:

    config_single_char.add_variable('tessedit_char_whitelist', 'QWERTYUIOPASDFGHJKLZXCVBNM')

### Read
The first parameter is always the configuration and the second parameter is always the image path

Read a pharese

<img src="http://i.imgur.com/BqO7Cqh.png">

    >>> LibTesseract.simple_read(config_line, 'phrase.png')
    the book is on the table

Read a pharese and say confidence in each sentence

<img src="http://i.imgur.com/PInL9bB.png">

    >>> LibTesseract.read_and_get_confidence_word(config_line, 'phrase.png')
    [('he', 82.19984436035156), ('is', 84.98550415039062), ('readlnq', 75.25213623046875), ('the', 74.60755157470703), ('book', 85.8053207397461)]

Read a char, say confidence and other possible characters

<img src="http://i.imgur.com/J26XnmD.png">

    >>> LibTesseract.read_and_get_confidence_char(config_single_char, 'char.png')
    [('E', 58.27500915527344), ('Y', 56.93630599975586), ('F', 56.4453125), ('T', 51.12168884277344), ('Q', 47.19916534423828), ('W', 46.1181640625), ('V', 45.31656265258789), ('G', 43.49636459350586)]
