# Problem Set 4A
# Name: <your name here>
# Collaborators:
# Time Spent: x:xx

import copy

def permutations_helper(current_list,str_left):
    if(len(str_left)==0):
        return
    letter=str_left[0]
    str_left=str_left[1:]
    dummy_current_list=copy.copy(current_list)
    for permutation in dummy_current_list:
        current_list.remove(permutation)
        current_list.append(letter+permutation)
        for i in range(len(permutation)):
            current_list.append(permutation[0:i+1]+letter+permutation[i+1:])
    permutations_helper(current_list,str_left)

def get_permutations(sequence):
    '''
    Enumerate all permutations of a given string

    sequence (string): an arbitrary string to permute. Assume that it is a
    non-empty string.  

    You MUST use recursion for this part. Non-recursive solutions will not be
    accepted.

    Returns: a list of all permutations of sequence

    Example:
    >>> get_permutations('abc')
    ['abc', 'acb', 'bac', 'bca', 'cab', 'cba']

    Note: depending on your implementation, you may return the permutations in
    a different order than what is listed here.
    '''
    final_list=[]
    final_list.append(sequence[0])
    sequence=sequence[1:]
    permutations_helper(final_list,sequence)
    final_list.sort()
    dummy_final_list=copy.copy(final_list)
    last_permutation=""
    for permutation in dummy_final_list:
        if(permutation==last_permutation):
            final_list.remove(permutation)
        last_permutation=permutation
    
    return final_list



if __name__ == '__main__':
    #EXAMPLE
    example_input = 'abc'
    print('Input:', example_input)
    print('Expected Output:', ['abc', 'acb', 'bac', 'bca', 'cab', 'cba'])
    print('Actual Output:  ', get_permutations(example_input))
    
    example_input = 'cde'
    print('Input:', example_input)
    print('Expected Output:', ['cde', 'ced', 'dce', 'dec', 'ecd', 'edc'])
    print('Actual Output:  ', get_permutations(example_input))
    
    example_input = 'acc'
    print('Input:', example_input)
    print('Expected Output:', ['acc', 'cac', 'cca'])
    print('Actual Output:  ', get_permutations(example_input))    
    
#    # Put three example test cases here (for your sanity, limit your inputs
#    to be three characters or fewer as you will have n! permutations for a 
#    sequence of length n)
    
    

