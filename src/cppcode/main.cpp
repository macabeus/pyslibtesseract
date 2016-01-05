#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>
#include <locale.h>


#define set_config(_config, _tesseract) \
    int _i;\
    for (_i = 0; _i < _config.variables_count; _i++) {\
        _tesseract->SetVariable(_config.variables->name, _config.variables->value);\
    }\
    _tesseract->SetPageSegMode(_config.psm);

#define tesseract_start(_image_dir, _tesseract) \
    setlocale(LC_NUMERIC, "C"); /* This line is necessary to avoid conflicts with other Python libraries such as matplotlib.pyplot */ \
    Pix *image_##_tesseract = pixRead(_image_dir);\
    \
    tesseract::TessBaseAPI *_tesseract = new tesseract::TessBaseAPI();\
    _tesseract->Init(NULL, config.lang);\
    _tesseract->SetImage(image_##_tesseract);\

#define tesseract_end(_tesseract) \
    _tesseract->End();\
    pixDestroy(&image_##_tesseract);

struct tesseract_variable {
    char* name;
    char* value;
};

struct tesseract_config {
    char lang[8];
    int variables_count;
    struct tesseract_variable* variables;
    tesseract::PageSegMode psm;
    bool get_hocr;
};

struct confidence_char {
    char letter;
    float percent;
};

struct confidence_word {
    char* word;
    float percent;
};

struct confidence_word_init {
    struct confidence_word* cw;
    int length;
};

extern "C" struct confidence_char* read_and_get_confidence_char(struct tesseract_config config, char* image_dir) {
    struct confidence_char* to_return = (struct confidence_char*) malloc(sizeof(confidence_char) * 30);
    to_return[0].letter = '\x00';

    tesseract_start(image_dir, tes_api)

    set_config(config, tes_api)

    tes_api->SetPageSegMode(tesseract::PSM_SINGLE_CHAR);
    tes_api->Recognize(NULL);
    int i = 0;
    tesseract::ResultIterator* ri = tes_api->GetIterator();
    tesseract::PageIteratorLevel level = tesseract::RIL_SYMBOL;
    if (ri != 0) {
        do {
            const char* symbol = ri->GetUTF8Text(level);
            if (symbol != 0) {
                tesseract::ChoiceIterator ci(*ri);
                do {
                    const char* choice = ci.GetUTF8Text();
                    to_return[i].letter = *choice;
                    to_return[i].percent = ci.Confidence();
                    i++;
                    to_return[i].letter = '\x00';
                } while(ci.Next());
            }
            delete[] symbol;
        } while((ri->Next(level)));
    }

    tesseract_end(tes_api)

    return to_return;
}

extern "C" struct confidence_word_init read_and_get_confidence_word(struct tesseract_config config, char* image_dir) {
    int max_length = 30;
    struct confidence_word_init my_return;
    my_return.cw = (struct confidence_word*) malloc(sizeof(confidence_word) * max_length);
    my_return.length = 0;

    tesseract_start(image_dir, tes_api)

    set_config(config, tes_api)

    tes_api->Recognize(0);
    tesseract::ResultIterator* ri = tes_api->GetIterator();
    if (ri != 0) {
        do {
            const char* word = ri->GetUTF8Text(tesseract::RIL_WORD);
            if (word != 0) {
                tesseract::ChoiceIterator ci(*ri);
                float conf = ri->Confidence(tesseract::RIL_WORD);
                my_return.cw[my_return.length].word = (char*) malloc(sizeof(char) * strlen(word));
                strcpy(my_return.cw[my_return.length].word, word);
                my_return.cw[my_return.length].percent = conf;

                my_return.length++;
                if (my_return.length == max_length) {
                    max_length += 100;
                    my_return.cw = (struct confidence_word*) realloc(my_return.cw, sizeof(confidence_word) * max_length);
                }
            }
            delete[] word;
        } while ((ri->Next(tesseract::RIL_WORD)));

        delete ri;
    }

    tesseract_end(tes_api)

    return my_return;
}

extern "C" char* simple_read(struct tesseract_config config, char* image_dir) {
    tesseract_start(image_dir, tes_api)

    set_config(config, tes_api)

    char* text;
    if (config.get_hocr) {
        text = tes_api->GetHOCRText(0);
    }  else {
        text = tes_api->GetUTF8Text();
    }
    char* buff = (char*) malloc((sizeof(char) * strlen(text)) + 1);
    strcpy(buff, text);
    delete[] text;

    tesseract_end(tes_api)

    return buff;
}

extern "C" void freeme(char* pointer) {
    free(pointer);
}
