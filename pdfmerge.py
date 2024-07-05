#!/usr/bin/env python

import os
import argparse
from pypdf import PdfWriter, PdfReader, PageObject, Transformation

INSIDE_MARGIN_RATIO  = 0.06
OUTSIDE_MARGIN_RATIO = 0.0

COLUMN_SPACING_RATIO = 0.0095
ROW_SPACING_RATIO    = 0.03

MARGIN_RATIO_TOP_TO_BOTTOM = 0.75

#==============================================================#
# Arguments
#==============================================================#
parser = argparse.ArgumentParser(
    description = 'convert 4 PDF pages to 1 PDF page.'
)

parser.add_argument(
    '-i', '--input', type=str, required = True,
    help = f'file path of input PDF'
)
parser.add_argument(
    '-o', '--output-fname', default='result.pdf', type=str,
    help = f'file name of output PDF [default: "result.pdf"]'
)
parser.add_argument(
    '-d', '--output-dirname', default='.', type=str,
    help = f'directory name of output PDF [default: "./"]'
)

parser.add_argument(
    '-t', f'--with-title', action = 'store_true',
    help=f'flag with title page'
)
parser.add_argument(
    f'--without-line', action = 'store_true',
    help=f'flag without column line'
)
parser.add_argument(
    f'--without-pagenum', action = 'store_true',
    help=f'flag without page number'
)
parser.add_argument(
    '--inside-margin', default=INSIDE_MARGIN_RATIO, type=float,
    help = f'inside margin ratio to page width [default: {INSIDE_MARGIN_RATIO}]'
)
parser.add_argument(
    '--outside-margin', default=OUTSIDE_MARGIN_RATIO, type=float,
    help = f'outside margin ratio to page width [default: {OUTSIDE_MARGIN_RATIO}]'
)
parser.add_argument(
    '--column-spacing', default=COLUMN_SPACING_RATIO, type=float,
    help = f'column spacing ratio to page width [default: {COLUMN_SPACING_RATIO}]'
)
parser.add_argument(
    '--row-spacing', default=ROW_SPACING_RATIO, type=float,
    help = f'row spacing ratio to page height [default: {ROW_SPACING_RATIO}]'
)
parser.add_argument(
    '--margin-ratio-top-to-bottom', default=MARGIN_RATIO_TOP_TO_BOTTOM, type=float,
    help = f'ratio of top margin to bottom margin [default: {MARGIN_RATIO_TOP_TO_BOTTOM}]'
)

args = parser.parse_args()


#==============================================================#
# i/o settings
#==============================================================#
input_pdf  = args.input
output_pdf = os.path.join( args.output_dirname, args.output_fname )
os.makedirs( args.output_dirname, exist_ok = True )

reader = PdfReader( input_pdf )
writer = PdfWriter()


#==============================================================#
# Dimension settings
#==============================================================#
_p = reader.pages[0]
WIDTH  = _p.mediabox.right
HEIGHT = _p.mediabox.top
INSIDE_MARGIN  = WIDTH * args.inside_margin
OUTSIDE_MARGIN = WIDTH * args.outside_margin

COLUMN_SPACING = WIDTH * args.column_spacing
ROW_SPACING    = HEIGHT * args.row_spacing

MINOR_WIDTH  = ( WIDTH - INSIDE_MARGIN - OUTSIDE_MARGIN - COLUMN_SPACING ) / 2
MINOR_HEIGHT = MINOR_WIDTH * ( HEIGHT / WIDTH )
MINOR_SCALE = MINOR_WIDTH / WIDTH
MINOR_SCALE_OP = dict(
    sx = MINOR_SCALE,
    sy = MINOR_SCALE
)

MARGIN_TOP_BOTTOM_SUM = ( HEIGHT - 2*MINOR_HEIGHT - ROW_SPACING )
_rtb = args.margin_ratio_top_to_bottom
MARGIN_TOP    = MARGIN_TOP_BOTTOM_SUM * ( _rtb / ( 1 + _rtb ) )
MARGIN_BOTTOM = MARGIN_TOP_BOTTOM_SUM * (    1 / ( 1 + _rtb ) )


#==============================================================#
# transformation props
#==============================================================#
UPPER_TY      = MARGIN_BOTTOM + MINOR_HEIGHT + ROW_SPACING
LOWER_TY      = MARGIN_BOTTOM
ODD_LEFT_TX   = INSIDE_MARGIN
ODD_RIGHT_TX  = INSIDE_MARGIN + MINOR_WIDTH + COLUMN_SPACING
EVEN_LEFT_TX  = OUTSIDE_MARGIN
EVEN_RIGHT_TX = OUTSIDE_MARGIN + MINOR_WIDTH + COLUMN_SPACING


#==============================================================#
# Other settings
#==============================================================#
WITH_TITLE_PAGE = args.with_title
TOTAL_PAGE_NUM = len( reader.pages )


#==============================================================#
# Procedures
#==============================================================#
def get_blank_page() -> type[PageObject]:
    return PageObject.create_blank_page(
        width  = WIDTH,
        height = HEIGHT
    )


def get_title_page() -> type[PageObject]:
    page = get_blank_page()
    _p = reader.pages[0]

    width  = WIDTH - INSIDE_MARGIN - OUTSIDE_MARGIN
    scale = width / WIDTH
    height = HEIGHT * scale
    op = Transformation().scale(
        sx = scale,
        sy = scale
    ).translate(
        tx = INSIDE_MARGIN,
        ty = ( HEIGHT - height ) / 2
    )
    _p.add_transformation( op )

    page.merge_page( _p )
    return page


def get_page( i: int ) -> type[PageObject]:
    """
    get the i-page PageObject from input PDF file.
    If `i` exceeds the total page of PDF, return a blank page.
    """
    is_blank = False
    if WITH_TITLE_PAGE:
        _i = i + 1
    else:
        _i = i

    is_blank = ( _i >= TOTAL_PAGE_NUM )
    if is_blank:
        return get_blank_page()
    else:
        return reader.pages[_i]


def get_transformation_props(
    tx: float = 0,
    ty: float = 0
) -> type[Transformation]:
    return Transformation().scale( **MINOR_SCALE_OP ).translate(
        tx = tx, ty = ty
    )


#==============================================================#
# Procedure for drawing line & page number
#==============================================================#
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

LINE_COLOR = ( 0, 0, 0 )
LINE_WIDTH = .1 * mm
ODD_LINE_X  = ODD_RIGHT_TX - COLUMN_SPACING/2
EVEN_LINE_X = EVEN_RIGHT_TX - COLUMN_SPACING/2

_DELTA_Y = MARGIN_TOP_BOTTOM_SUM / 20
LINE_YS = (
    UPPER_TY + MINOR_HEIGHT + _DELTA_Y,
    LOWER_TY - _DELTA_Y
)
FONT_PROPS = ( 'Helvetica', 10 )

def get_canvas_page(
    is_odd: bool,
    page_num: str
) -> type[PageObject]:
    buffer = BytesIO()

    cc = canvas.Canvas( buffer, pagesize = A4 )

    line_x = ODD_LINE_X if is_odd else EVEN_LINE_X

    if not args.without_line:
        cc.setStrokeColorRGB( *LINE_COLOR )
        cc.setLineWidth( LINE_WIDTH )
        cc.line(
            x1 = line_x, y1 = LINE_YS[0],
            x2 = line_x, y2 = LINE_YS[1]
        )

    if not args.without_pagenum:
        cc.setFont( *FONT_PROPS )
        cc._setExtGState
        cc.drawCentredString(
            x = line_x,
            y = MARGIN_BOTTOM * 0.3,
            text = page_num,
        )

    cc.showPage()
    cc.save()
    return PdfReader( buffer ).pages[0]


#==============================================================#
# Title & blank page
#==============================================================#
if WITH_TITLE_PAGE:
    _total_page_num = TOTAL_PAGE_NUM - 1
    writer.add_page( get_title_page() )
    writer.add_page( get_blank_page() )
else:
    _total_page_num = TOTAL_PAGE_NUM


#==============================================================#
# Main
#==============================================================#
print( f' > Start marging PDF files' )
for i in range( 0, _total_page_num, 4 ):
    print( f'   * page {i}' )

    page_num = i // 4 + 1
    is_odd = i % 8 == 0

    pages = [
        get_page( i ),
        get_page( i + 1 ),
        get_page( i + 2 ),
        get_page( i + 3 )
    ]

    page = get_blank_page()

    #==============================================================#
    # transformation
    #==============================================================#
    upper_ty = UPPER_TY
    lower_ty = LOWER_TY
    if is_odd:
        left_tx  = ODD_LEFT_TX
        right_tx = ODD_RIGHT_TX
    else:
        left_tx  = EVEN_LEFT_TX
        right_tx = EVEN_RIGHT_TX

    pages[0].add_transformation( get_transformation_props(
        tx = left_tx,
        ty = upper_ty
    ))
    pages[1].add_transformation( get_transformation_props(
        tx = left_tx,
        ty = lower_ty
    ))
    pages[2].add_transformation( get_transformation_props(
        tx = right_tx,
        ty = upper_ty
    ))
    pages[3].add_transformation( get_transformation_props(
        tx = right_tx,
        ty = lower_ty
    ))

    for j in range(4):
        page.merge_page( pages[j] )


    #==============================================================#
    # Line & pagenum
    #==============================================================#
    if not args.without_line or not args.without_pagenum:
        canvas_page = get_canvas_page(
            is_odd   = is_odd,
            page_num = str( page_num )
        )
        page.merge_page( canvas_page )


    #==============================================================#
    # add page
    #==============================================================#
    writer.add_page( page )


    #==============================================================#
    # Line (failed)
    #==============================================================#
    # from pypdf.annotations import PolyLine
    # line_x = ODD_LINE_X if is_odd else EVEN_LINE_X
    # annotation = PolyLine(
    #     vertices = [ ( line_x, LINE_YS[0] ), ( line_x, LINE_YS[1] ) ]
    # )
    # writer.add_annotation(
    #     page_number = writer.get_num_pages() - 1,
    #     annotation = annotation
    # )


with open( output_pdf, mode = 'wb' ) as f:
    writer.write( f )
    print( f' > Export to "{output_pdf}".' )
