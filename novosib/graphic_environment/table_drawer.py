from PIL import Image, ImageDraw, ImageFont
from graphic_environment.conf import OUTLINE_WIDTH, INLINE_WIDTH, SMALLEST_STRING
from graphic_environment.conf import C_RED, C_GREEN, C_GREY
from graphic_environment.conf import RED_TAGS, GREEN_TAGS, GREY_TAGS

class TableDrawer:
    # TODO remove do_results - bad code
    # TODO слишком много строк, разделить на подфункции
    @staticmethod
    def draw_table(board, font_size, path_to_pic, color_matrix=None, double_cells=None, results=None):
        # calculates the width and height of image
        params = TableDrawer.board_params(board, font_size, double_cells)
        x_size = len(params[0])
        y_size = len(params[1])
        width = OUTLINE_WIDTH * 2 + INLINE_WIDTH * (len(params[0]) - 1)
        height = OUTLINE_WIDTH * 2 + INLINE_WIDTH * (len(params[1]) - 1)
        for cell_width in params[0]:
            width += cell_width
        for cell_height in params[1]:
            height += cell_height
        img = Image.new('RGB', (width, height), color='white')

        # region drawing outlines (borders) and inlines
        # outlines
        indent = (OUTLINE_WIDTH - 1) / 2
        draw = ImageDraw.Draw(img)
        draw.line((0, indent, width, indent), fill=0, width=OUTLINE_WIDTH)
        draw.line((0, height - indent - 1, width, height - indent - 1), fill=0, width=OUTLINE_WIDTH)
        draw.line((indent, 0, indent, height), fill=0, width=OUTLINE_WIDTH)
        draw.line((width - indent - 1, 0, width - indent - 1, height), fill=0, width=OUTLINE_WIDTH)

        # inlines
        start_pix = OUTLINE_WIDTH - int((INLINE_WIDTH + 1) / 2)
        shift = 0
        for x in range(x_size - 1):
            shift += params[0][x] + INLINE_WIDTH
            draw.line((start_pix + shift, 0, start_pix + shift, height), fill=0, width=INLINE_WIDTH)
        shift = 0
        for y in range(y_size - 1):
            shift += params[1][y] + INLINE_WIDTH
            draw.line((0, start_pix + shift, width, start_pix + shift), fill=0, width=INLINE_WIDTH)
        # endregion

        # region coloring cells if board_color is not None
        if color_matrix is not None:
            if color_matrix == 'default':
                color_matrix = TableDrawer.create_default_color_matrix(board)
            start_pix = OUTLINE_WIDTH
            shift_x = 0
            shift_y = 0
            for x in range(x_size):
                shift_y = 0
                for y in range(y_size):
                    seed = (start_pix + shift_x, start_pix + shift_y)
                    shift_y += params[1][y] + INLINE_WIDTH
                    if (type(color_matrix[y][x]) is tuple) and (len(color_matrix[y][x]) == 3):
                        ImageDraw.floodfill(img, seed, color_matrix[y][x])
                        continue
                    if color_matrix[y][x] in GREY_TAGS:
                        ImageDraw.floodfill(img, seed, C_GREY)
                    if color_matrix[y][x] in GREEN_TAGS:
                        ImageDraw.floodfill(img, seed, C_GREEN)
                    if color_matrix[y][x] in RED_TAGS:
                        ImageDraw.floodfill(img, seed, C_RED)
                shift_x += params[0][x] + INLINE_WIDTH
        # endregion

        # region printing text
        fnt = ImageFont.truetype('times.ttf', font_size)
        start_pix = OUTLINE_WIDTH
        shift_x = 0
        shift_y = 0
        for x in range(x_size):
            shift_y = 0
            for y in range(y_size):
                fnt_seed = (start_pix + shift_x + params[0][x] / 2, start_pix + shift_y + params[1][y] / 2)
                shift_y += params[1][y] + INLINE_WIDTH
                draw.text(fnt_seed, str(board[y][x]), font=fnt, fill=0, anchor='mm')
            shift_x += params[0][x] + INLINE_WIDTH
        # endregion

        TableDrawer.post_print(draw, font_size // 2, params, double_cells)

        if results is not None:
            small_fnt = ImageFont.truetype('times.ttf', font_size // 3)
            l_x, t_y, r_x, b_y = TableDrawer.get_cell_corners(x_size - 1, y_size - 1, params)
            width, height = r_x - l_x, b_y - t_y
            small_seed = (l_x - 1 + width / 6, t_y - 1 + height / 6)
            big_seed = (l_x - 1 + width * 3 / 5, t_y - 1 + height / 2)
            draw.text(small_seed, 'Всего', font=small_fnt, fill=0, anchor='mm')
            draw.text(big_seed, str(results), font=fnt, fill=0, anchor='mm')

        # img.show()
        img.save(path_to_pic, 'PNG')
        return path_to_pic

    # TODO make this work
    @staticmethod
    def print_text(draw: ImageDraw, box, font_size, text_params, fill=0, anchor='mm'):
        if type(text_params) is tuple:
            for word_params in text_params:
                word = str(word_params[0])
                w_fnt_size = word_params[1]

    @staticmethod
    def post_print(draw, font_size, params, double_cells=None):
        if double_cells is None:
            return
        fnt = ImageFont.truetype('times.ttf', font_size)
        for d_cell in double_cells:
            c_x, c_y = d_cell[0], d_cell[1]
            word_bot, word_top = d_cell[2], d_cell[3]
            l_x, t_y, r_x, b_y = TableDrawer.get_cell_corners(c_x, c_y, params)
            draw.line((l_x, t_y, r_x, b_y), fill=0, width=INLINE_WIDTH)
            bot_seed = (l_x - 1 + (r_x - l_x) / 4, t_y - 1 + (b_y - t_y) * 3 / 4)
            top_seed = (l_x - 1 + (r_x - l_x) * 3 / 4, t_y - 1 + (b_y - t_y) / 4)
            draw.text(bot_seed, str(word_bot), font=fnt, fill=0, anchor='mm')
            draw.text(top_seed, str(word_top), font=fnt, fill=0, anchor='mm')

    @staticmethod
    def get_cell_corners(c_x, c_y, params):
        start_pix = OUTLINE_WIDTH
        shift_x = start_pix
        shift_y = start_pix
        for x in range(c_x):
            shift_x += params[0][x] + INLINE_WIDTH
        for y in range(c_y):
            shift_y += params[1][y] + INLINE_WIDTH
        return (shift_x, shift_y, shift_x + params[0][c_x], shift_y + params[1][c_y])

    # TODO слишком много строк, разделить на подфункции
    @staticmethod
    def board_params(board, font_size, double_cells=None):
        # first array in params stands for x-size of cells, second for y-size
        # x and y are inverted because board is transposed to x-y basis
        params = [[], []]
        fnt = ImageFont.truetype('times.ttf', font_size)
        x_len = len(board)
        y_len = len(board[0])

        # d_cell = [x-coord, y-coord, bottom word, top word]
        double_matrix = [['' for i in range(y_len)] for j in range(x_len)]
        if double_cells is not None:
            half_fnt = ImageFont.truetype('times.ttf', font_size // 2)
            for d_cell in double_cells:
                c_x, c_y = d_cell[0], d_cell[1]
                word_bot, word_top = d_cell[2], d_cell[3]
                box_bot, box_top = half_fnt.getbbox(str(word_bot)), half_fnt.getbbox(str(word_top))
                max_box_x, max_box_y = max(box_bot[2], box_top[2]), max(box_bot[3], box_top[3])
                double_matrix[c_x][c_y] = (max_box_x, max_box_y)

        for y in range(y_len):
            max_x = fnt.getbbox(SMALLEST_STRING)[2]
            for x in range(x_len):
                if double_matrix[x][y] != '':
                    word_size = 2 * double_matrix[x][y][0]
                else:
                    word = str(board[x][y])
                    word_size = fnt.getbbox(word.lower())[2]
                if word_size > max_x:
                    max_x = word_size
            params[0].append(max_x)
        for x in range(x_len):
            max_y = fnt.getbbox(SMALLEST_STRING)[3]
            for y in range(y_len):
                if double_matrix[x][y] != '':
                    word_size = 2 * double_matrix[x][y][1]
                else:
                    word = str(board[x][y])
                    word_size = fnt.getbbox(word.lower())[3]
                if word_size > max_y:
                    max_y = word_size
            params[1].append(max_y)

        # resizes params arrays to make cells square if they look like high rectangle (x < y)
        min_y = 1000000
        for x in range(x_len):
            if params[1][x] < min_y:
                min_y = params[1][x]
        for y in range(y_len):
            if params[0][y] < min_y:
                params[0][y] = min_y

        # makes cells larger to fit the text with gaps
        for y in range(y_len):
            params[0][y] += 2 * int(font_size // 4)
        for x in range(x_len):
            params[1][x] += 2 * int(font_size // 4)

        return params

    # TODO make this work
    @staticmethod
    def get_box_size(text_params, font_size):
        width, height = 0, 0
        x_segments = []
        y_segments = []
        for word_params in text_params:
            x_segment, y_segment = [], []
            word = str(word_params[0])
            l_x, t_y, r_x, b_y = word_params[1]
            fnt_scale = word_params[2]
            anchor = word_params[3]
            fnt = ImageFont.truetype('times.ttf', font_size / fnt_scale)
            box = fnt.getbbox(word)

    # default coloring - colors in green, red or gey and works only for int
    # >0 - green, ==0 - grey, <0 - red, else - grey
    # TODO добавить Enum с этими параметрами
    @staticmethod
    def create_default_color_matrix(board):
        color_matrix = [[0 for i in range(len(board[0]))] for j in range(len(board))]
        for x in range(len(board)):
            for y in range(len(board[0])):
                if type(board[x][y]) is int:
                    if board[x][y] < 0:
                        color_matrix[x][y] = C_RED
                    if board[x][y] > 0:
                        color_matrix[x][y] = C_GREEN
                else:
                    color_matrix[x][y] = C_GREY
        return color_matrix

    # default empty matrix: 0 - empty, 1 - print text
    # in default '' or ' ' in board stands for empty
    # old, probably useless method !OLD!
    @staticmethod
    def create_default_empty_matrix(board):
        empty_matrix = [[0 for i in range(len(board[0]))] for j in range(len(board))]
        for x in range(len(board)):
            for y in range(len(board[0])):
                if board[x][y] in ['', ' ']:
                    empty_matrix[x][y] = 0
                else:
                    empty_matrix[x][y] = 1
        return empty_matrix


