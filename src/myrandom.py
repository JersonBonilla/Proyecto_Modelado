'''
Module that includes the linear congruential generator (LCG)
and each distribution function needed.
'''

import math

class LCG:
    '''Class that represents a linear congruential generator (LCG).'''

    def __init__(self, seed=123456789):
        '''
        Initializes a processor.

        :param seed: Seed used to generate numbers.
        '''

        self.a = 1664525  # Multiplier.
        self.c = 1013904223  # Increment. 
        self.m = 2**32  # Module. 
        self.seed = seed  # Seed being used.

    def rand(self):
        '''Generate a pseudorandom number in [0, 1).'''

        self.seed = (self.a * self.seed + self.c) % self.m
        return self.seed / self.m


# Global instance of an LCG to reuse the generator.
lcg = LCG()


def uniform(a, b):
    '''
    Generates an uniform random variable in [a, b].

    :param a: Lower limit.
    :param b: Upper limit.
    :return: Random value.
    '''
    return a + (b - a) * lcg.rand()


def expovariate(lambd):
    '''
    Generate an exponential random variable with a λ parameter.

    :param lambd: Arrival rate (λ).
    :return: random value.
    '''
    
    u = lcg.rand()
    return -1 / lambd * math.log(1 - u)


def triangular(low, mode, high):
    '''
    Generate a triangular random variable.

    :param low: Minimum value possible.
    :param mode: Most likely value.
    :param high: Maximum value possible.
    :return: random value.
    '''

    u = lcg.rand()
    c = (mode - low) / (high - low)
    if u < c:
        return low + ((high - low) * c * u) ** 0.5
    else:
        return high - ((high - low) * (1 - u) * (1 - c)) ** 0.5



def gauss(mu, sigma):
    '''
    Generates a normal random variable using convolution of 
    12 uniform variables.

    :param mu: Mean.
    :param sigma: Standard deviation.
    :return: random value.
    '''
    
    return mu + sigma * (sum(lcg.rand() for _ in range(12)) - 6)


def c3_processing_time():
    '''
    Generate a processing time for C3 with the specific function.
    '''
    while True:
        x = uniform(3, 5)  # Generate candidate value.
        y = uniform(0, 1)  # Generate random height.

        # Accept if it is under f(x).
        if y <= (3 * x ** 2 / 98): 
            return x  


def c3_arrival_time():
    '''
    Generate a time between arrivals for C3 using acceptance-rejection method
    for the custom triangular-like distribution specified in the problem statement.
    '''
    while True:
        x = uniform(2, 10)  # Candidate value in the range
        y = uniform(0, 0.25)  # Max density is 0.25

        # Evaluate real density at x
        if 2 <= x <= 4:
            fx = x / 8 - 0.25
        elif 4 < x <= 10:
            fx = 5 / 12 - x / 24
        else:
            fx = 0  # Out of bounds (just in case)

        if y <= fx:
            return x