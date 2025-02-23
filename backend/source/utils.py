import random



def generate_otp() -> str:
    otp = ""
    for i in range(7):
        otp += str(random.randint(1, 9))
    return otp



def myprint(*args):
    for i in args:
        print("\n", i, "\n")