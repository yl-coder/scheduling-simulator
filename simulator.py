'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import queue as queue

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
#Based on assumption that when the job end at t = 5, process arriving at t = 5 is already at the ready queue.
def RR_scheduling(process_list, time_quantum ):

    schedule = []
    current_time = 0
    waiting_time = 0

    pq = queue.PriorityQueue()

    for process in process_list:
        # (arrive_time, cur_job_end_time(to make sure it process after job arriving at cur_job_end_time is processed first), id, burst_time, waiting_time)
        pq.put((process.arrive_time, 0, process.id, process.burst_time, 0))


    while not pq.empty():
        process = list(pq.get())
        if current_time < process[0]:
            current_time = process[0]
        schedule.append((current_time, process[2]))
        process[4] = process[4] + (current_time - process[0])
        next_arr_time = current_time + time_quantum
        if process[3] > time_quantum:
            process[0] = next_arr_time
            process[3] = process[3] - time_quantum
            process[1] = next_arr_time
            pq.put(tuple(process))
        else:
            next_arr_time = current_time + process[3]
            waiting_time += process[4]
        current_time = next_arr_time

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):

    schedule = []
    current_time = 0
    waiting_time = 0

    # pq = queue.PriorityQueue()

    processes = []

    for process in process_list:
        # (arrive_time, cur_job_end_time(to make sure it process after job arriving at cur_job_end_time is processed first), id, burst_time, waiting_time)
        processes.append((process.burst_time, process.arrive_time, process.id))
        # pq.put((process.burst_time, process.arrive_time, process.id))

    processes.sort()

    while len(processes) != 0:
        suitable_slot = False
        for i in range(len(processes)):
            process = processes[i]
            if process[1] <= current_time:
                schedule.append((current_time, process[2]))
                current_time += process[0]
                waiting_time += current_time - process[1]
                processes.pop(i)
                suitable_slot = True
                break
        if not suitable_slot:
            current_time += 1

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time


def SJF_scheduling(process_list, alpha):

    schedule = []
    current_time = 0
    waiting_time = 0

    #Store the predicted value of process, default guess is 5
    predicted = {}
    for process in process_list:
        predicted[process.id] = 5

    #Modified structure to store the processes
    processes = []

    for process in process_list:
        # (arrive_time, cur_job_end_time(to make sure it process after job arriving at cur_job_end_time is processed first), id, burst_time, waiting_time)
        processes.append([5, process.arrive_time, process.burst_time, process.id])
        # pq.put((process.burst_time, process.arrive_time, process.id))

    processes.sort()

    while len(processes) != 0:
        suitable_slot = False
        for i in range(len(processes)):
            process = processes[i]
            if process[1] <= current_time:
                schedule.append((current_time, process[3]))
                current_time += process[2]
                waiting_time += current_time - process[1]
                processes.pop(i)
                suitable_slot = True
                #Modify the processes queue and sort it again
                processId = process[3]
                predicted[processId] = (alpha * process[2]) + ((1 - alpha) * predicted[processId])
                for c in range(len(processes)):
                    processes[c][0] = predicted[processes[c][3]]
                processes.sort()
                break
        if not suitable_slot:
            current_time += 1

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 5)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])