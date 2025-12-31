# to generate otp like 'K8gY5c'
#using random module in python we can generate otp 
#random -> used to generate a random number
#choice -> used to generate a random letters
import random
def genotp():
    otp=''
    u_l = [chr(i) for i in range(ord('A'),ord('Z')+1)]
    s_l = [chr(i) for i in range(ord('a'),ord('z')+1)]
    for i in range(0,2):
        otp = otp + random.choice(u_l) + str(random.randint(0,9)) + random.choice(s_l)
    return otp

    