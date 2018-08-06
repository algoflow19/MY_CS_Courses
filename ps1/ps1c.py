annual_salary = float(input("Enter the starting salary:​"))
total_cost = 1000000
semi_annual_raise = .07
portion_down_payment=0.25
r = 0.04 # Intereing rate for inverestment.


def isCouldBuyHouse(staring_salary,saved_rated):
    current_salary=staring_salary
    current_savings=0;
    current_mouths=0;
    for i in range(0,36):
        current_savings+=saved_rated*current_salary/12+current_savings*r/12
        current_mouths+=1;
        if(current_mouths%6==0):
            current_salary+=current_salary*semi_annual_raise
        if(current_savings>total_cost*portion_down_payment):
            return True;
    return False;

precision = 10000
max=precision
min=0

if(not isCouldBuyHouse(annual_salary,1.0)):
    print("It is not possible to pay the down payment in three years.\n")
    exit()
beserachSteps=0
while( max - min >1):
    beserachSteps+=1
    current=int((max+min)/2)
    if(isCouldBuyHouse(annual_salary,float(current)/precision)):
        max=current
    else:
        min=current


print("Best savings rate: %.4f" %(float(max)/precision))
print("Steps in bisection search:​ %d" %beserachSteps)