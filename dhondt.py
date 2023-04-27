import numpy as np
from typing import List

def dhondt(votes, seats):
    votes = np.asarray(votes)
    seat_count = int(seats)
    seats = np.zeros(votes.size, dtype=int)
    for seat_number in range(seat_count):
        quotients = votes / (seats + 1)
        i = np.argmax(quotients)
        seats[i] += 1
    return seats


def dhondt_ittifak(ittifaks: List[int], seats: int):
    # divide seats between ittifaks
    ittifak_count = len(ittifaks)
    seats_per_ittifak = np.zeros(ittifak_count, dtype=int)
    sums_ittifak = [sum(ittifak) for ittifak in ittifaks]
    dhondt_result = dhondt(sums_ittifak, seats)

    # distribute seats inside ittifak
    copy_of_ittifaks = ittifaks.copy()
    for i in range(ittifak_count):
        copy_of_ittifaks[i] = dhondt(ittifaks[i], dhondt_result[i])

    return copy_of_ittifaks



def test_dhondt():
    votes = [100000, 80000, 30000]
    seats = 10
    result = dhondt(votes, seats)
    print(result)


def test_dhondt_ittifak():
    ittifaks = [[100000, 80000, 30000], [50000, 40000, 10000]]
    seats = 10
    result = dhondt_ittifak(ittifaks, seats)
    print(result)


if __name__ == "__main__":
    # test_dhondt()
    test_dhondt_ittifak()

