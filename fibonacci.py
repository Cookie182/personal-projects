def fibonacci():
    while True:
        try:  # to get valid input
            num = int(input('Enter the number for fibonacci: '))
            break
        except:
            print('Enter a valid positive integer!\n')
            continue

    nums = [0, 1]  # initial 2 fibonacci valules
    if num in nums:
        return num

     # this loop gets the next fibonacci number while removing the first value    in the list
    for x in range(num - 1):
        nums.append(nums[-1] + nums[-2])  # getting next fibonacci
        nums.pop(0)  # to keep list size constant
    return 'Fibonnaci squence number {0} = {1}\n'.format(num, "{:,}".format(nums[-1]))


# loop to ask user if they want to try the function again
print(fibonacci())
while True:
    try_again = input('Do you want to try again? [Y]: ')
    if try_again.lower() == 'y':
        print(fibonacci())
        continue
    else:
        print('Thank you for trying the program!')
        break
