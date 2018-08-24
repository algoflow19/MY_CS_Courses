def insertion_sort(A):
    result = A.copy()
    for i in range(1, len(result)):
        cur_value = result[i]
        j = i - 1
        while j >= 0 and result[j] > cur_value:
            result[j+1] = result[j]
            j -= 1
        result[j+1] = cur_value
    return result

def merge(L, R):
    result = []
    l_idx, r_idx = (0, 0)
    while l_idx < len(L) and r_idx < len(R):
        if L[l_idx] < R[r_idx]:
            result.append(L[l_idx])
            l_idx += 1
        else:
            result.append(R[r_idx])
            r_idx += 1
    result.extend(L[l_idx:len(L)])
    result.extend(R[r_idx:len(R)])
    return result

def mergesort(A):
    if len(A) <= 1:
        return A
    n = len(A)
    L = mergesort(A[0:n//2])  # // uses integer division
    R = mergesort(A[n//2:n])
    return merge(L, R)
