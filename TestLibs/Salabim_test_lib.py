import salabim as sim

N = 3 # число каналов (касс)
R = 7 # обслуживание + очередь
LIMIT = 5000 # остановка 5000
SER = 500 # статистика каждые 500 обслуживаний вывод
SEED = 1
ANIMATE = True


def report_ser(waits, selected):
    # среднее время ожидания
    first = sum(waits) / len(waits)
    # средний квадрат отклонения
    dis = sum((x - first) ** 2 for x in waits) / len(waits)
    print(f"ns = {selected}: w = {first:.6f}, D = {dis:.6f}")


def change_population(model, delta):
    # учёт времени в состояниях r
    now = model.env.now()
    model.state_time[model.in_system] += now - model.last_change
    model.last_change = now
    model.in_system += delta
    # Monitor.tally(): фиксирует число в системе
    model.population_monitor.tally(model.in_system)


# наследование от встроенного Component
class Customer(sim.Component):
    def setup(self, model, arrival):
        self.model = model
        self.arrival = arrival


    def process(self):
        m = self.model
        # request() использует Resource и его FIFO-очередь
        yield self.request(m.servers)
        x = m.env.now() - self.arrival
        m.selected += 1
        m.waits.append(x)
        if len(m.waits) == SER:
            report_ser(m.waits, m.selected)
            m.waits.clear()

        if m.selected == LIMIT:
            m.finished = True
            # пробуждаем главный компонент, чтобы env.run() завершился
            # main - не наш, а встроенный, используется для немедленной остановки run
            m.env.main().activate()
            return

        # Exponential.sample() - встроенное распределение
        # hold() планирует окончание обслуживания
        yield self.hold(m.service_dist.sample())
        # release() освобождает канал, очередь продвигается сама
        self.release(m.servers)
        change_population(m, -1)


class ArrivalGenerator(sim.Component):
    def setup(self, model):
        self.model = model


    def process(self):
        m = self.model

        while not m.finished:
            # Exponential.sample() + hold() формируют прибытие Z
            yield self.hold(m.arrival_dist.sample())
            if m.finished:
                return

            if m.in_system >= R:
                m.refused += 1
                continue

            change_population(m, +1)
            # создание Component запускает процесс новой заявки
            Customer(model = m, arrival = m.env.now())


class Model:
    def __init__(self, env):
        self.env = env
        # Resource() - каналы обслуживания и очередь
        self.servers = sim.Resource(name = "servers", capacity = N)
        # встроенные экспоненциальные распределения
        self.arrival_dist = sim.Exponential(mean = 1.0)
        self.service_dist = sim.Exponential(mean = 1.0)
        # начальные значения счётчиков и статистики
        self.in_system = 0
        # level = True - монитор значения во времени
        self.population_monitor = sim.Monitor(name = "Заявок в системе", level = True)
        self.population_monitor.tally(0)
        self.last_change = 0.0
        self.state_time = [0.0] * (R + 1)
        self.selected = 0
        self.refused = 0
        self.waits = []
        self.finished = False


def show_graph(m):
    # текстовая гистограмма долей времени по числу заявок
    print("Гистограмма состояний системы (встроенный Monitor salabim):")
    m.population_monitor.print_histogram()


def main():
    sim.yieldless(False)
    # генератор случайных чисел библиотеки
    sim.random_seed(SEED)
    # Environment() - календарь событий, T=0
    env = sim.Environment()
    m = Model(env)
    ArrivalGenerator(model = m)

    # AnimateMonitor - встроенный график количества заявок от времени
    if ANIMATE:
        sim.AnimateMonitor(
            monitor=m.population_monitor,
            title="Заявок в системе во времени",
            x=70, y=100, width=850, height=350,
            horizontal_scale=0.3, vertical_scale=30,
            linecolor="blue", linewidth=2,
        )

        sim.AnimateText(
            text="Модельное время T",
            x=500,
            y=30,
            fontsize=16
        )

        sim.AnimateText(
            text="Количество заявок в системе",
            x=30,
            y=180,
            fontsize=16,
            angle=90
        )

        # параметры окна и синхронизация с временем
        env.animation_parameters(synced=True, speed=50, width=1000, height=550)
        env.animate(True)

    env.run()

    T = env.now()
    m.state_time[m.in_system] += T - m.last_change
    print(f"Итог: T = {T:.6f}, ns = {m.selected}, отказов = {m.refused}")
    for r,duration in enumerate(m.state_time):
        print(f"p[{r}]={duration / T:.6f}")
    print(f"Сумма вероятностей={sum(m.state_time) / T:.6f}")
    # дополнительная статистика встроенного Resource salabim
    print(f"Средняя занятость каналов: {m.servers.occupancy.mean():.6f}")
    show_graph(m)


if __name__ == "__main__":
    main()