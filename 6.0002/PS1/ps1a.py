###########################
# 6.0002 Problem Set 1a: Space Cows 
# Name:
# Collaborators:
# Time:

from ps1_partition import get_partitions
import time
import copy
#================================
# Part A: Transporting Space Cows
#================================

# Problem 1
def load_cows(filename):
    """
    Read the contents of the given file.  Assumes the file contents contain
    data in the form of comma-separated cow name, weight pairs, and return a
    dictionary containing cow names as keys and corresponding weights as values.

    Parameters:
    filename - the name of the data file as a string

    Returns:
    a dictionary of cow name (string), weight (int) pairs
    """
    cows_dict={}
    file = open(filename,'r')
    for line in file:
        tmp_list=line.split(',')
        cows_dict[tmp_list[0]]=int(tmp_list[1])
    file.close() # On...
    return cows_dict

# Problem 2
def greedy_cow_transport(cows,limit=10):
    """
    Uses a greedy heuristic to determine an allocation of cows that attempts to
    minimize the number of spaceship trips needed to transport all the cows. The
    returned allocation of cows may or may not be optimal.
    The greedy heuristic should follow the following method:

    1. As long as the current trip can fit another cow, add the largest cow that will fit
        to the trip
    2. Once the trip is full, begin a new trip to transport the remaining cows

    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)
    
    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """
    to_carry_cows=[]
    total_list=[]
    cows_list=[]
    for cow in cows:
        cows_list.append((cow,cows[cow]))
    cows_list=sorted(cows_list,key=lambda x:x[1],reverse=True)
    sum=0
    
    current_trip_list=[]
    total_list=[]
    while(len(cows_list)!=0):
        sum=0
        for cow in cows_list:
            if(sum+cow[1]<=limit):
                current_trip_list.append(cow[0])
                sum+=cow[1]
        total_list.append(current_trip_list)
        for cow_name in current_trip_list:
            cows_list.remove((cow_name,cows[cow_name]))
        current_trip_list=[]
    
    return total_list

def is_trip_possible(trips,limit):
    """
    trip: A possible cows trip, containing serval trips(weight)
    limit: Every trip limit weight
    RETURN: True if the given could be done, otherwise False.
    """
    for trip in trips:
        if(sum(trip)>limit):
            return False
    return True


# Problem 3
def brute_force_cow_transport(cows,limit=10):
    """
    Finds the allocation of cows that minimizes the number of spaceship trips
    via brute force.  The brute force algorithm should follow the following method:

    1. Enumerate all possible ways that the cows can be divided into separate trips 
        Use the given get_partitions function in ps1_partition.py to help you!
    2. Select the allocation that minimizes the number of trips without making any trip
        that does not obey the weight limitation
            
    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)
    
    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """
    cows_dict={}
    print(cows)
    for i in range(1,11):
        cows_dict[i]=[]
    cows_name_list=[]
    for cow in cows:
        cows_name_list.append(cow)
        cows_dict[cows[cow]].append(cow)
    
    def translate_name2num(cows_list):
        for i in cows_list:
            if(type(i)==type([])):
                cows_list.remove(i)
                cows_list.insert(0,translate_name2num(i))
            elif(cows.get(i,-1)!=-1):
                cows_list.remove(i)
                cows_list.insert(0,cows.get(i,-1))
        return cows_list
    
    trip_generator=get_partitions(cows_name_list)
    trip_generator=list(trip_generator)
    trip_generator=translate_name2num(trip_generator)
    
    for trips in sorted(trip_generator,key=len):
        if(is_trip_possible(trips,limit)):
            trip_found=trips 
            break
    trips_result=[]
    for trip in map( lambda x: list(map( lambda cow: cows_dict[cow].pop(0) ,x)),trip_found):
        trips_result.append(trip)   
    return trips_result

# Problem 4
def compare_cow_transport_algorithms():
    """
    Using the data from ps1_cow_data.txt and the specified weight limit, run your
    greedy_cow_transport and brute_force_cow_transport functions here. Use the
    default weight limits of 10 for both greedy_cow_transport and
    brute_force_cow_transport.
    
    Print out the number of trips returned by each method, and how long each
    method takes to run in seconds.

    Returns:
    Does not return anything.
    """
    cows=load_cows("ps1_cow_data.txt")
    start1=time.time()
    greed_result=greedy_cow_transport(cows)
    end1=time.time()
    start2=time.time()
    print(cows)
    force_result=brute_force_cow_transport(cows)
    end2=time.time()
    print("The greedy algorithm takes %fs, it result is:" %(end1-start1),greed_result)
    print("The brute force algorithm takes %fs, it result is:" %(end2-start2),force_result)
    

#print(brute_force_cow_transport( {"Jesse": 6, "Maybel": 3, "Callie": 2, "Maggie": 5}))
#print(greedy_cow_transport({"Jesse": 6, "Maybel": 3, "Callie": 2, "Maggie": 5}))
compare_cow_transport_algorithms()
