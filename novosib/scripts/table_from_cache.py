from solution_cache import SolutionCache
from task_cache import TaskCache
from player_cache import PlayerCache
from collections import defaultdict
from graphic_environment.table_drawer import TableDrawer
from util import calculate_points
from conf_krestiki import CENTER_EXTRA_BONUS, IS_YELLOW_MAX, YELLOW_COLOR
from scripts.conf_tables import TABLE_NAME, PATH

def table_from_cache(player, player_cache: PlayerCache, solution_cache: SolutionCache, tasks_cache: TaskCache, path_to_pic=None):
    # player <=> user_id
    mask = [[0, 0, 0, 0, 0] for i in range(5)]
    theme_mask = defaultdict()
    i = 0
    tour = player_cache.players_storage[str(player)].tour
    for theme in tasks_cache.tours[tour]:
        theme_mask[theme] = i
        i += 1
    for sol in solution_cache.solution_storage:
        if sol[0] == str(player):
            if tasks_cache.check_task(tour, sol[1], sol[2], sol[3]):
                mask[theme_mask[sol[1]]][int(sol[2]) - 1] = 1
            else:
                mask[theme_mask[sol[1]]][int(sol[2]) - 1] = -1

    board = [['', '', '', '', ''] for i in range(5)]
    for x in range(5):
        for y in range(5):
            if (mask[x][y] == -1):
                board[x][y] = 0
            elif (mask[x][y] == 1):
                board[x][y] = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if x + i >= 0 and x + i < 5 and y + j >= 0 and y + j < 5 and i * j == 0:
                            board[x][y] += (mask[x + i][y + j] == 1)
                board[x][y] += CENTER_EXTRA_BONUS * (x == 2 and y == 2 and mask[x][y] == 1)
    
    c_matrix = [['', '', '', '', ''] for i in range(5)]
    for x in range(5):
        for y in range(5):
            if board[x][y] == '':
                continue
            if board[x][y] >= 1:
                if board[x][y] >= 5 and IS_YELLOW_MAX:
                    c_matrix[x][y] = YELLOW_COLOR
                else:
                    c_matrix[x][y] = 'green'
            elif board[x][y] <= 0:
                c_matrix[x][y] = 'red'

    if path_to_pic == None:
        path_to_pic = PATH + TABLE_NAME
    ok, points = calculate_points(player, tour, solution_cache, tasks_cache)
    path = TableDrawer.draw_table(board, 36, path_to_pic=path_to_pic, color_matrix=c_matrix)
    return True, path, TABLE_NAME, points
