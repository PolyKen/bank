import asyncio
import inspect

color_dict = {"red": "31", "green": "32",
              "yellow": "33", "blue": "34", "purple": "35"}


def colorize(string, color):
    colored = "\033[" + color_dict[color] + "m" + string + "\033[0m"
    return colored


red = lambda s: colorize(s, "red")
yellow = lambda s: colorize(s, "yellow")
green = lambda s: colorize(s, "green")
blue = lambda s: colorize(s, "blue")


def async_run_tasks(coro_func_list, para_list):
    loop = asyncio.get_event_loop()
    tasks = []
    if type(coro_func_list) is not list:
        coro_func_list = [coro_func_list] * len(para_list)
    for i, func in enumerate(coro_func_list):
        para = para_list[i]
        coro = func(*para)
        task = loop.create_task(coro)
        tasks.append(task)
    loop.run_until_complete(asyncio.wait(tasks))
    tasks_results = [task.result() for task in tasks]
    return tasks_results
