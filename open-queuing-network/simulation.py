from multiprocessing import Pool
from os import sched_getaffinity

from network_statistics import QueueNetwork

def get_quantitative_stats(
    network: QueueNetwork,
    worker_processes: tuple[int, int]
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Get steady-state statistics for a range of arrival rates.

    Args:
        network: A QueueNetwork instance.
        worker_processes: The number of worker processes to use for
            process pools that parallelize the execution of the methods
            responsible for computing network statistics.

    Returns:
        Theoretical and simulated averages for each subsystem in the
        network for each number of intermediate queues up to network.n
        for each arrival rate in network.arrival_rates.
    """
    cpu_pool_1, cpu_pool_2 = worker_processes
    start_end = tuple((rate, 1) for rate in network.arrival_rates)
    sim_iter, theor_iter = (), ()
    for i in range(1, network.n + 1):
        middle = tuple((rate, i) for rate in network.arrival_rates)
        theor_iter += middle
        sim_iter += start_end + middle + start_end
    with Pool(processes = cpu_pool_1) as p1, Pool(processes = cpu_pool_2) as p2:
        theor_results = p1.starmap_async(network.mm1_queue_theoretical_stats,
                                         theor_iter)
        sim_results = p2.starmap_async(network.mm1_queue_sim_stats, sim_iter)
        return (theor_results.get(), sim_results.get())

def get_comparative_stats(
    network: QueueNetwork,
    theor_stats: list[tuple[float, float]],
    sim_stats: list[tuple[float, float]],
    worker_processes: int
) -> list[list[tuple[float, float]]]:
    """Get differences between theoretical and simulated statistics.

    Args:
        network: A QueueNetwork instance.
        theor_stats: Theoretical, steady-state averages for each
            subsystem in the network for each number of intermediate
            queues up to network.n for each arrival rate in
            network.arrival_rates.
        sim_stats: Simulated, steady-state averages for each subsystem
            in the network for each number of intermediate queues up to
            network.n for each arrival rate in network.arrival_rates.
        worker_processes: The number of worker processes to use for the
            process pool that parallelizes the execution of the method
            responsible for computing differences between statistics.

    Returns:
        Absolute differences between simulated averages and their
        corresponding theoretical averages for each arrival rate for
        each subsystem in the network for each number of intermediate
        queues.
    """
    starmap_iter = []
    for i in range(3 * network.n):
        start = i * len(network.arrival_rates)
        end = (i + 1) * len(network.arrival_rates)
        sim_stats_slice = sim_stats[start:end]
        if not (i - 1) % 3:
            start = ((i - 1) // 3) * len(network.arrival_rates)
            end = ((i - 1) // 3 + 1) * len(network.arrival_rates)
            theor_stats_slice = theor_stats[start:end]
        else:
            theor_stats_slice = theor_stats[:len(network.arrival_rates)]
        starmap_iter.append((theor_stats_slice, sim_stats_slice))
    with Pool(processes = worker_processes) as p:
        return p.starmap(network.mm1_queue_comparative_stats, starmap_iter)

def get_quantitative_figures(network: QueueNetwork,
                             theor_stats: list[tuple[float, float]],
                             sim_stats: list[tuple[float, float]],
                             worker_processes: int) -> None:
    """Get figures displaying steady-state statistics for the network.

    Args:
        network: A QueueNetwork instance.
        theor_stats: Theoretical averages for each subsystem in the
            network for each number of intermediate queues up to
            network.n for each arrival rate in network.arrival_rates.
        sim_stats: Simulated averages for each subsystem in the
            network for each number of intermediate queues up to
            network.n for each arrival rate in network.arrival_rates.
        worker_processes: The number of worker processes to use for the
            process pool that parallelizes the execution of the method
            responsible for creating quantitative figures.
    """
    starmap_iter = []
    for i in range(1, network.n + 1):
        start = (i - 1) * len(network.arrival_rates)
        end = i * len(network.arrival_rates)
        starmap_iter.append((theor_stats[:len(network.arrival_rates)],
                             theor_stats[start : end],
                             sim_stats[start * 3 : end * 3],
                             i))
    with Pool(processes = worker_processes) as p:
        p.starmap(network.create_quantitative_charts, starmap_iter)

def get_comparative_figures(network: QueueNetwork,
                            comparative_stats: list[list[tuple[float, float]]],
                            worker_processes: int) -> None:
    """Get figures displaying differences between network averages.

    Args:
        network: A QueueNetwork instance.
        comparative_stats: Absolute differences between simulated
            averages and their corresponding theoretical averages for
            each arrival rate in network.arrival_rates for each
            subsystem in the network for each number of intermediate
            queues up to network.n.
        worker_processes: The number of worker processes to use for the
            process pool that parallelizes the execution of the method
            responsible for creating comparative figures.
    """
    starmap_iter = []
    for i in range(3):
        if i == 1:
            subsystem = '2_1'
        else:
            subsystem = i + 1
        starmap_iter.append([subsystem] + comparative_stats[i::3])
    with Pool(processes = worker_processes) as p:
        p.starmap(network.create_comparative_charts, starmap_iter)

def main() -> None:
    """Get theoretical and simulated averages for a queueing network.

    Provision worker processes for parallel programming, and get
    statistics and figures for an open queueing network whose queues are
    treated as M/M/1 systems via the application of Kleinrock's
    Independence Approximation.
    """
    cpu_pool = cpu_pool_1 = cpu_pool_2 = 1
    if len(sched_getaffinity(0)) > 2:
        cpu_pool = len(sched_getaffinity(0)) - 1
    if len(sched_getaffinity(0)) > 3:
        cpu_pool_1 = cpu_pool_2 = (len(sched_getaffinity(0)) - 1) // 2
        if not len(sched_getaffinity(0)) % 2:
            cpu_pool_2 += 1
    network = QueueNetwork(4, 60000, tuple(range(50, 1201, 50)),
                           8000, 10 * (10**6))
    mm1_theoretical_stats, mm1_sim_stats = get_quantitative_stats(
        network, (cpu_pool_1, cpu_pool_2))
    comparative_stats = get_comparative_stats(network, mm1_theoretical_stats,
                                              mm1_sim_stats, cpu_pool)
    get_quantitative_figures(network, mm1_theoretical_stats,
                             mm1_sim_stats, cpu_pool)
    get_comparative_figures(network, comparative_stats, cpu_pool)


if __name__ == "__main__":
    main()
