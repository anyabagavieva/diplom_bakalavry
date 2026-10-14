import matplotlib.pyplot as plt
import random
import simpy

N = 3 # число каналов (касс)
R = 7 # обслуживание + очередь
LIMIT = 5000 # остановка 5000
SER = 500 # статистика каждые 500 обслуживаний вывод
SEED = 1


def report_ser(waits, selected):
    # среднее время ожидания
    first = sum(waits) / len(waits)
    # средний квадрат отклонения
    dis = sum((x - first) ** 2 for x in waits) / len(waits)
    print(f"ns = {selected}: w = {first:.6f}, D = {dis:.6f}")


def change_population(env, data, delta):
    # время в состояниях системы
    data["state_time"][data["in_system"]] += env.now - data["last_change"]
    data["last_change"] = env.now
    data["in_system"] += delta
    data["history_time"].append(env.now)
    data["history_count"].append(data["in_system"])


def customer(env, servers, arrival, data, stop):
    # функция, представляющая одну принятую заявку
    # Resource.request() ставит заявку в FIFO-очередь, если нет доступных каналов
    with servers.request() as request:
        yield request
        # env.now — текущее модельное время
        x = env.now - arrival
        data["selected"] += 1
        data["waits"].append(x)
        if len(data["waits"]) == SER:
            report_ser(data["waits"], data["selected"])
            data["waits"].clear()

        if data["selected"] == LIMIT:
            # Event.succeed() инициирует остановку env.run() по достижению максимального числа
            stop.succeed()
            return
        # timeout() назначает событие завершения обслуживания
        yield env.timeout(random.expovariate(1))
    # при выходе из with ресурс освобождается автоматически
    change_population(env, data, -1)


def arrivals(env, servers, data, stop):
    # генератор поступлений, пока модель не остановится
    while True:
        # timeout() формирование следующего события прибытия Z
        yield env.timeout(random.expovariate(1))
        if data["in_system"] >= R:
            data["refused"] += 1
            continue
        change_population(env, data, +1)
        # env.process() создаёт процесс принятой заявки
        env.process(customer(env, servers, env.now, data, stop))


def show_graph(state_time, T):
    # график вероятностей состояний системы
    prob = [duration / T for duration in state_time]
    states = range(len(prob))

    plt.figure(figsize = (9, 5))
    plt.bar(states, prob)
    plt.xticks(list(states))
    plt.xlabel("К-во заявок в системе")
    plt.ylabel("Доля времени в состояниях")
    plt.title("Вероятности состояний системы")
    plt.grid(axis = "y", alpha = 0.3)
    plt.tight_layout()
    plt.show()


def show_population_over_time(times, counts, T):
    # число заявок в системе от модельного времени
    plt.figure(figsize = (9, 5))
    plt.step(times + [T], counts + [counts[-1]], where = "post")
    plt.xlabel("Модельное время T")
    plt.ylabel("Количество заявок в системе")
    plt.yticks(range(R + 1))
    plt.ylim(-0.5, R + 0.5)
    plt.xlim(0, T)
    plt.grid(alpha = 0.3)
    plt.title("Изменение количества заявок по времени")
    plt.tight_layout()
    plt.show()


def main():
    random.seed(SEED)
    # Environment() создаёт время T=0 и календарь событий
    env = simpy.Environment()
    # Resource() обеспечивает N каналов и FIFO-очередь
    servers = simpy.Resource(env, capacity = N)
    # Event() - событие завершения моделирования
    stop = env.event()
    data = {
        "in_system": 0,
        "last_change": 0.0,
        "state_time": [0.0] * (R + 1),
        "selected": 0,
        "refused": 0,
        "waits": [],
        "history_time": [0.0], # моменты изменения числа заявок
        "history_count": [0] # число заявок в эти моменты
    }

    env.process(arrivals(env, servers, data, stop))
    # run(until=event) запуск моделирования
    env.run(until = stop)
    T = env.now

    data["state_time"][data["in_system"]] += T - data["last_change"]
    print(f"Итог: T = {T:.6f}, ns = {data['selected']}, отказов = {data['refused']}")
    for r,duration in enumerate(data["state_time"]):
        print(f"p[{r}]={duration / T:.6f}")
    print(f"Сумма вероятностей={sum(data['state_time']) / T:.6f}")
    print(f"Занято каналов: {servers.count}; в очереди: {len(servers.queue)}")
    show_graph(data["state_time"], T)
    show_population_over_time(data["history_time"], data["history_count"], T)


if __name__ == "__main__":
    main()