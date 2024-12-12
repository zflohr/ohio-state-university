from math import log as ln
from multiprocessing import Pool
from os import sched_getaffinity
from random import uniform

import matplotlib.pyplot as plt

class QueueNetwork:

    def __init__(self, intermediate_nodes: int, packet_transmissions: int,
                 arrival_rates: tuple[int | float, ...],
                 avg_packet_len: int | float, link_capacity: int) -> None:
        """Initialize the queue network.

        Args:
            intermediate_nodes: The maximum number of intermediate
                forwarding nodes.
            packet_transmissions: The number of packets transmitted
                throughout the queueing network.
            arrival_rates: Arrival rates (in packets/s) to simulate at
                the entry node to the network.
            avg_packet_len: The average length of a packet (in bits) in
                the network.
            link_capacity: The rate (in bits/s) whereat data is
                transmitted from the entry node to the intermediate
                nodes.
        """
        self.n = intermediate_nodes
        self.transmissions = packet_transmissions
        self.arrival_rates = arrival_rates
        self.avg_packet_len = avg_packet_len
        self.link_capacity = link_capacity

    def _random_exp_number(self, rate: int | float) -> float:
        """Generate a random number from an exponential distribution.

        Use the inverse transformation method to generate exponentially
        distributed random numbers from the cumulative distribution
        function of the exponential distribution.

        Args:
            rate: The rate of the exponential distribution.

        Returns:
            An exponentially distributed random number with distribution
            mean of 1 / rate.
        """
        return -ln(uniform(0, 1)) / rate

    def mm1_queue_theoretical_stats(self, arrival_rate: int | float,
                                    n: int) -> tuple[float, float]:
        """Compute theoretical statistics for an M/M/1 queueing system.

        Use the following queueing theory equations for M/M/1 systems to
        calculate averages at steady state for the subsystem under
        investigation:

            E[N] = λ / (μ - λ)
            E[T] = 1 / (μ - λ)

        Args:
            arrival_rate: The rate (in packets/s) whereat packets arrive
                at the queueing subsystem under investigation.
            n: The total number of intermediate nodes in the network
                that contains the queueing subsystem under
                investigation.

        Returns:
            The average number of packets and average packet delay in
            the M/M/1 queueing subsystem at theoretical steady state for
            the given arrival rate and number of intermediate nodes in
            the network.
        """
        arrival_rate = arrival_rate / n
        service_rate = self.link_capacity / n / self.avg_packet_len
        theoretical_avg_packet_num = arrival_rate/(service_rate-arrival_rate)
        theoretical_avg_packet_delay = (1/(service_rate-arrival_rate)) * 1000
        return (theoretical_avg_packet_num, theoretical_avg_packet_delay)

    def mm1_queue_sim_stats(self, arrival_rate: int | float,
                            n: int) -> tuple[float, float]:
        """Compute steady-state statistics for an M/M/1 queueing system.

        Transmit self.transmissions packets through the subsystem to
        simulate steady state.

        Args:
            arrival_rate: The rate (in packets/s) whereat packets arrive
                at the queueing subsystem under investigation.
            n: The total number of intermediate nodes in the network
                that contains the queueing subsystem under
                investigation.

        Returns:
            The average number of packets and average packet delay in
            the M/M/1 queueing subsystem at simulated steady state for
            the given arrival rate and number of intermediate nodes in
            the network.
        """
        arrival_rate = arrival_rate / n
        service_rate = self.link_capacity / n / self.avg_packet_len
        sys_arrival_time, sys_wait_time = 0, 0
        accum_sys_wait_time, sys_departure_time = 0, 0
        for packet in range(1, self.transmissions + 1):
            interarrival_time = self._random_exp_number(arrival_rate)
            service_time = self._random_exp_number(service_rate)
            sys_arrival_time += interarrival_time
            if sys_arrival_time <= sys_departure_time:
                sys_wait_time += service_time - interarrival_time
            else:
                sys_wait_time = service_time
            accum_sys_wait_time += sys_wait_time
            sys_departure_time = sys_arrival_time + sys_wait_time
        sim_avg_packet_num = accum_sys_wait_time / sys_departure_time
        sim_avg_packet_delay = accum_sys_wait_time * 1000 / self.transmissions
        return (sim_avg_packet_num, sim_avg_packet_delay)

    def mm1_queue_comparative_stats(
        self,
        theor_stats: list[tuple[float, float]],
        sim_stats: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        """Compute differences between theoretical and simulated stats.

        Args:
            theor_stats: Theoretical, steady-state averages for each
                arrival rate in self.arrival_rates for a subsystem in
                the network.
            sim_stats: Simulated, steady-state averages for each arrival
                rate in self.arrival_rates for a subsystem in the
                network.

        Returns:
            The absolute difference between each simulated average and
            the corresponding theoretical average for each arrival rate
            for the subsystem of interest.
        """
        diffs = []
        for i in range(len(self.arrival_rates)):
            sim_avg_packet_num, sim_avg_packet_delay = sim_stats[i]
            theor_avg_pack_num, theor_avg_pack_delay = theor_stats[i]
            num_diff = abs(sim_avg_packet_num - theor_avg_pack_num)
            delay_diff = abs(sim_avg_packet_delay - theor_avg_pack_delay)
            diffs.append((num_diff, delay_diff))
        return diffs

    def create_comparative_charts(
        self,
        subsystem: int,
        *subsystem_avg_diffs: list[tuple[float, float]]
    ) -> None:
        """Create a figure showing differences between subsystem stats.

        Create a figure showing absolute differences between theoretical
        and simulated averages for a subsystem at steady state, and save
        the figure to a PDF file in the current directory.

        Args:
            subsystem: The subsystem of interest.
            *subsystem_avg_diffs: Absolute differences between
                simulated, steady-state averages and their corresponding
                theoretical, steady-state averages for each arrival rate
                for a subsystem in the network for each number of
                intermediate queues up to self.n. The number of
                arguments passed should equal self.n.
        """
        fig, axs = plt.subplots(2, 1)
        fig.subplots_adjust(hspace=0.7)
        fig.set_size_inches(10, 9)
        cmap = plt.get_cmap('viridis', len(subsystem_avg_diffs))
        axs[0].set_xlabel('Lambda (packets/s)')
        axs[0].set_ylabel('Absolute difference in Number of Packets')
        axs[1].set_xlabel('Lambda (packets/s)')
        axs[1].set_ylabel('Absolute difference in Delay Time (ms)')
        axs[0].set_title(f'Subsystem {subsystem}')
        axs[1].set_title(f'Subsystem {subsystem}')
        for i, avg_diffs in enumerate(subsystem_avg_diffs):
            pack_num_diffs = [diffs[0] for diffs in avg_diffs]
            pack_delay_diffs = [diffs[1] for diffs in avg_diffs]
            axs[0].plot(self.arrival_rates, pack_num_diffs,
                        label = f'n = {i + 1}', color = cmap(i))
            axs[1].plot(self.arrival_rates, pack_delay_diffs,
                        label = f'n = {i + 1}', color = cmap(i))
        axs[0].legend(fontsize = 8, loc = 'upper left')
        axs[1].legend(fontsize = 8, loc = 'upper left')
        fig.savefig(f'comparative_charts_subsystem_{subsystem}.pdf',
                    format = 'pdf')

    def create_quantitative_charts(
        self,
        network_entry_exit_theor_stats: list[tuple[float, float]],
        intermediate_queue_theor_stats: list[tuple[float, float]],
        network_sim_stats: list[tuple[float, float]],
        n: int) -> None:
        """Create a figure containing subplots showing queue statistics.

        Create a figure showing theoretical and simulated statistics for
        a queueing network at steady state, and save the figure to a PDF
        file in the current directory.

        Args:
            network_entry_exit_theor_stats: Theoretical, steady-state
                averages for the entry and exit nodes of the queueing
                network for all arrival rates in self.arrival_rates.
            intermediate_queue_theor_stats: Theoretical, steady-state
                averages for one intermediate node for all arrival rates
                in self.arrival_rates when the queueing network has n
                intermediate nodes.
            network_sim_stats: Simulated, steady-state averages for the
                entire queueing network (entry node, exit node, and one
                intermediate node) for all arrival rates in
                self.arrival_rates when the network has n intermediate
                nodes.
            n: The number of intermediate nodes in the queueing network.
        """
        fig, axs = plt.subplots(3, 2)
        fig.suptitle(f'Number of intermediate queues (n) = {n}')
        fig.subplots_adjust(hspace=0.7)
        fig.set_size_inches(10, 9)
        for i in range(3):
            queue_sim_stats = network_sim_stats[
                i * len(self.arrival_rates) : (i + 1) * len(self.arrival_rates)]
            queue_sim_avg_packet_num = [stats[0] for stats in queue_sim_stats]
            queue_sim_avg_packet_delay = [stats[1] for stats in queue_sim_stats]
            axs[i][0].plot(self.arrival_rates, queue_sim_avg_packet_num,
                     label = 'Simulated Average Packet Number',
                     color = 'blue', linestyle = '--')
            axs[i][1].plot(self.arrival_rates, queue_sim_avg_packet_delay,
                     label = 'Simulated Delay Time',
                     color = 'blue', linestyle = '--')
            axs[i][0].set_xlabel('Lambda (packets/s)')
            axs[i][0].set_ylabel('Number of packets')
            axs[i][1].set_xlabel('Lambda (packets/s)')
            axs[i][1].set_ylabel('Delay Time (ms)')
            if i == 1:
                intermediate_queue_theor_avg_packet_num = [
                    stats[0] for stats in intermediate_queue_theor_stats]
                intermediate_queue_theor_avg_packet_delay = [
                    stats[1] for stats in intermediate_queue_theor_stats]
                axs[i][0].plot(self.arrival_rates,
                         intermediate_queue_theor_avg_packet_num,
                         label = 'Theoretical Average Packet Number',
                         color = 'blue', linestyle = '-')
                axs[i][1].plot(self.arrival_rates,
                         intermediate_queue_theor_avg_packet_delay,
                         label = 'Theoretical Delay Time',
                         color = 'blue', linestyle = '-')
                axs[i][0].set_title(f'Subsystem {i + 1},1')
                axs[i][1].set_title(f'Subsystem {i + 1},1')
            else:
                network_entry_exit_theor_avg_packet_num = [
                    stats[0] for stats in network_entry_exit_theor_stats]
                network_entry_exit_theor_avg_packet_delay = [
                    stats[1] for stats in network_entry_exit_theor_stats]
                axs[i][0].plot(self.arrival_rates,
                         network_entry_exit_theor_avg_packet_num,
                         label = 'Theoretical Average Packet Number',
                         color = 'blue', linestyle = '-')
                axs[i][1].plot(self.arrival_rates,
                         network_entry_exit_theor_avg_packet_delay,
                         label = 'Theoretical Delay Time',
                         color = 'blue', linestyle = '-')
                axs[i][0].set_title(f'Subsystem {i + 1}')
                axs[i][1].set_title(f'Subsystem {i + 1}')
            axs[i][0].legend(fontsize = 8, loc = 'upper left')
            axs[i][1].legend(fontsize = 8, loc = 'upper left')
        fig.savefig(f'quantitative_charts_{n}.pdf', format = 'pdf')

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

if __name__ == "__main__":
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
