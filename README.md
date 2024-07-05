# pdfmerge-4to1page

## Prerequisites
`pypdf` and `reportlab` are required.
```
$ pip install pypdf
$ pip install reportlab
```

## Usage
```
$ python pdfmerge_4to1.py [options]
```

### Options
```
usage: pdfmerge_4to1.py [-h] -i INPUT
  [-o OUTPUT_FNAME] [-d OUTPUT_DIRNAME] [-t] [--without-line]
  [--without-pagenum] [--inside-margin INSIDE_MARGIN]
  [--outside-margin OUTSIDE_MARGIN] [--column-spacing COLUMN_SPACING]
  [--row-spacing ROW_SPACING]
  [--margin-ratio-top-to-bottom MARGIN_RATIO_TOP_TO_BOTTOM]

convert 4 PDF pages to 1 PDF page.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        file path of input PDF
  -o OUTPUT_FNAME, --output-fname OUTPUT_FNAME
                        file name of output PDF [default: "result.pdf"]
  -d OUTPUT_DIRNAME, --output-dirname OUTPUT_DIRNAME
                        directory name of output PDF [default: "./"]
  -t, --with-title      flag with title page
  --without-line        flag without column line
  --without-pagenum     flag without page number
  --inside-margin INSIDE_MARGIN
                        inside margin ratio to page width [default: 0.06]
  --outside-margin OUTSIDE_MARGIN
                        outside margin ratio to page width [default: 0.0]
  --column-spacing COLUMN_SPACING
                        column spacing ratio to page width [default: 0.0095]
  --row-spacing ROW_SPACING
                        row spacing ratio to page height [default: 0.03]
  --margin-ratio-top-to-bottom MARGIN_RATIO_TOP_TO_BOTTOM
                        ratio of top margin to bottom margin [default: 0.75]
```
