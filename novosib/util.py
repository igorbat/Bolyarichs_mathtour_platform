from solution_cache import SolutionCache
from task_cache import TaskCache
from collections import defaultdict
from conf_krestiki import CENTER_EXTRA_BONUS
import codecs


def calculate_points(player, tour, solution_cache: SolutionCache, tasks_cache: TaskCache):
    # player <=> user_id
    points = 0
    mask = [[0, 0, 0, 0, 0] for i in range(5)]
    theme_mask = {}
    i = 0
    for theme in tasks_cache.tours[tour]:
        theme_mask[theme] = i
        i += 1
    for sol in solution_cache.solution_storage:
        if sol[0] == str(player):
            if tasks_cache.check_task(tour, sol[1], sol[2], sol[3]):
                mask[theme_mask[sol[1]]][int(sol[2]) - 1] = 1
            else:
                mask[theme_mask[sol[1]]][int(sol[2]) - 1] = -1
    
    for x in range(5):
        for y in range(5):
            if (mask[x][y] == 1):
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if x + i >= 0 and x + i < 5 and y + j >= 0 and y + j < 5 and i * j == 0:
                            points += (mask[x + i][y + j] == 1)
                points += CENTER_EXTRA_BONUS * (x == 2 and y == 2 and mask[x][y] == 1)
    return (True, f'Ваше число очков: {points}')


def generate_html(solutions, tasks, players):
    results = defaultdict(list)
    for playerr in players.players_storage:
        player = players.players_storage[playerr]
        if not player.allowed:
            continue
        tour = player.tour
        fio = player.fio
        fio = fio.replace('\n', ', ')
        points = 0
        sols = 0
        corrects_sols = 0
        for sol in solutions.solution_storage:
            if sol[0] == player.user_id:
                sols += 1
                if tasks.check_task(tour, sol[1], sol[2], sol[3]):
                    points += int(sol[2]) * 10
                    corrects_sols += 1
        results[tour].append([fio, points, corrects_sols, sols])

    for tour in results:
        sorted_res = sorted(results[tour], key=lambda x: -x[1])
        with codecs.open(tour + '_res.html', 'w', "utf-8") as f:
            f.write("<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"><title>{}</title></head>\n<body>".format(tour))
            f.write("<div>очков задач посылок место название </div>")
            for _, mass in enumerate(sorted_res):
                f.write("<div><pre>" + str(mass[1]).ljust(6, " ") + str(mass[2]).ljust(6, " ") +
                        str(mass[3]).ljust(8, " ") + str(_ + 1).ljust(6, " ") + mass[0] + "</pre></div>")
            f.write("</body></html>")


def generate_html_bonuses(solutions, tasks, players):
    player_results = defaultdict(list)
    for playerr in players.players_storage:
        player = players.players_storage[playerr]
        if not player.allowed:
            continue
        tour = player.tour
        fio = player.fio
        fio = fio.replace('\n', ', ')
        if tour == "pro":
            mapp = []
            for i in range(4):
                mapp.append([0, 0, 0, 0, 0])
        else:
            mapp = []
            for i in range(7):
                mapp.append([0, 0, 0, 0, 0])
        
        player_results[player.user_id] = [fio, 0, 0, 0, tour, mapp]
    
    mapper = {
        "pro":
            {
                "pro_div":0,
                "pro_rabbit":1,
                "pro_color":2,
                "pro_text":3
            },
        "novice":
            {
                "quest":0,
                "text":1,
                "math":2,
                "chess":3,
                "sudoku": 4,
                "problem": 5,
                "logic": 6
            }
    }
    uniq_bonuses = {
        "pro":
            {
                "pro_div":0,
                "pro_rabbit":0,
                "pro_color":0,
                "pro_text":0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0
            },
        "novice":
            {
                "quest":0,
                "text":0,
                "math":0,
                "chess":0,
                "sudoku":0,
                "problem":0,
                "logic":0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0
            }
    }
    for sol in solutions.solution_storage:
        player_results[sol[0]][3] += 1
        if tasks.check_task(player_results[sol[0]][4], sol[1], sol[2], sol[3]):
            player_results[sol[0]][1] += int(sol[2]) * 10
            player_results[sol[0]][2] += 1
            player_results[sol[0]][5][mapper[player_results[sol[0]][4]][sol[1]]][int(sol[2]) - 1] = 1

            sum_theme = sum(player_results[sol[0]][5][mapper[player_results[sol[0]][4]][sol[1]]])
            sum_number = 0
            for theme in player_results[sol[0]][5]:
                sum_number += theme[int(sol[2]) - 1]
            
            if sum_theme == 5:
                player_results[sol[0]][1] += 50
                print("Player {} took bonus in theme: {}".format(sol[0] + player_results[sol[0]][0], sol[1]))
                if uniq_bonuses[player_results[sol[0]][4]][sol[1]] == 0:
                    player_results[sol[0]][1] += 50
                    print("Player {} took first bonus in theme: {}".format(sol[0] + player_results[sol[0]][0], sol[1]))
                    uniq_bonuses[player_results[sol[0]][4]][sol[1]] = 1
            
            if sum_number == len(mapper[player_results[sol[0]][4]]):
                player_results[sol[0]][1] += int(sol[2]) * 10
                print("Player {} took bonus in theme: {}, tour = {}".format(sol[0] + player_results[sol[0]][0], sol[2], player_results[sol[0]][4]))
                if uniq_bonuses[player_results[sol[0]][4]][int(sol[2])] == 0:
                    player_results[sol[0]][1] += int(sol[2]) * 10
                    print("Player {} took first bonus in theme: {}, tour = {}".format(sol[0] + player_results[sol[0]][0], sol[2], player_results[sol[0]][4]))
                    uniq_bonuses[player_results[sol[0]][4]][int(sol[2])] = 1
    
    results = defaultdict(list)
    for playert in player_results:
        player = player_results[playert]
        results[player[4]].append([player[0], player[1], player[2], player[3]])

    for tour in results:
        sorted_res = sorted(results[tour], key=lambda x: -x[1])
        with codecs.open(tour + '_res_bonuses.html', 'w', "utf-8") as f:
            f.write("<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"><title>{}</title></head>\n<body>".format(tour))
            f.write("<div>очков задач посылок место название </div>")
            for _, mass in enumerate(sorted_res):
                if mass[3] > 0:
                    f.write("<div><pre>" + str(mass[1]).ljust(6, " ") + str(mass[2]).ljust(6, " ") +
                            str(mass[3]).ljust(8, " ") + str(_ + 1).ljust(6, " ") + mass[0] + "</pre></div>")
            f.write("</body></html>")
