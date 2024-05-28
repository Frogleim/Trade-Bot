import math
import random


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def modular_exponentiation(base, exponent, modulus):
    result = 1
    base = base % modulus
    while exponent > 0:
        if (exponent % 2) == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus
    return result


def shor_classical(N):
    if N % 2 == 0:
        return 2

    for i in range(5):  # Try a few times to get a non-trivial factor
        a = random.randint(2, N - 1)
        gcd_value = gcd(a, N)
        if gcd_value > 1:
            return gcd_value

        # Quantum part (period finding) would go here, but we simulate with random guess
        r = random.randint(1, N)

        # Check if r is even
        if r % 2 != 0:
            continue

        x = modular_exponentiation(a, r // 2, N)
        if x == N - 1 or x == 1:
            continue

        factor1 = gcd(x + 1, N)
        factor2 = gcd(x - 1, N)

        if factor1 == 1 or factor1 == N:
            continue

        return factor1, factor2

    return None


N = 88888888888888888888888  # Number to factorize
factors = shor_classical(N)
if factors:
    print(f"Factors of {N} are {factors}")
else:
    print(f"Failed to find factors of {N}")
