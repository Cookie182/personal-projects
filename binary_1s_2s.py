def int_to_binary(n, compliment_1s=False, compliment_2s=False):
    binary_n = []

    bits = []
    current_bit = 1
    while current_bit <= n:
        bits.append(current_bit)
        current_bit *= 2
    bits.reverse()

    for bit in bits:
        if bit <= n:
            binary_n.append('1')
            n -= bit
        else:
            binary_n.append('0')

    # convert to 1s compliment
    if compliment_1s == True:
        for x in range(len(binary_n)):
            if binary_n[x] == '1':
                binary_n[x] = '0'
            else:
                binary_n[x] = '1'

        int_1s = 0
        for _ in range(len(binary_n)):
            int_1s += (bits[_] * int(binary_n[_]))
        return f"{''.join(binary_n)} -> {int_1s}"

    # convert to 2s compliment
    if compliment_2s == True:
        for x in range(len(binary_n)):
            if binary_n[x] == '1':
                binary_n[x] = '0'
            else:
                binary_n[x] = '1'

        # sorting out the first bit (from the right) using the +1 carryon
        add_carryone = 0
        first_one = 1
        int_2s = 0

        # adjusting if first bit is 1 and applying +1 carryon and rest of the addition depending on if carryon is again +1 or +0
        if binary_n[-1] == '1':
            binary_n[-1] = '0'
            first_one = 0
            add_carryone = 1

            # starting from second bit (from the right) and applying binary addition
            for _ in range(-2, (0 - len(binary_n) - 1), -1):
                # base case break rule
                if add_carryone == 0:
                    break

                if binary_n[_] == '1':
                    binary_n[_] = '0'
                else:
                    binary_n[_] = '1'
                    add_carryone = 0

            # fringe case
            if add_carryone == 1:
                binary_n.append('1')

            for _ in range(len(bits)):
                int_2s += (bits[_] * int(binary_n[_]))
            return f"{''.join(binary_n)} -> {int_2s}"

        # simple case if first bit (from the right) is 0
        else:
            binary_n[-1] = '1'
            first_one = 0
            for _ in range(len(bits)):
                int_2s += (bits[_] * int(binary_n[_]))
            return f"{''.join(binary_n)} -> {int_2s}"

    return f"{''.join(binary_n)}"


n = int(input("Enter integer: "))
print("Binary form:", int_to_binary(n))
print("1s compliment:", int_to_binary(n, compliment_1s=True))
print("2s compliment:", int_to_binary(n, compliment_2s=True))
