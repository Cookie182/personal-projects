def password(uppercase=0, lowercase=0, digits=0, punctuation=0, amount=1, extra=None) -> str:
    import random
    import string
    passwords = []

    for x in [uppercase, lowercase, digits, punctuation, amount]:
        if type(x) != int:
            raise TypeError + 'Invalid input type'
    if type(extra) != str:
        extra = str(extra)

    for p in range(amount):
        password = []
        chars = set()
        if p == 0:
            print("======================================")
        else:
            print('\n=====================================')
        print("Password no.", p + 1)

        if uppercase > 0:  # choosing uppercase characters
            for _ in range(uppercase):
                char = random.choice(string.ascii_uppercase)
                chars.add(char)
                password.append(char)
            print("Uppercases chosen:", *chars)
            chars.clear()

        if lowercase > 0:  # choosing lowercase characters
            for _ in range(lowercase):
                char = random.choice(string.ascii_lowercase)
                chars.add(char)
                password.append(char)
            print("Lowercases chosen:", *chars)
            chars.clear()

        if digits > 0:  # choosing digit characters
            for _ in range(digits):
                char = random.choice(string.digits)
                chars.add(char)
                password.append(char)
            print("Digits chosen:", *chars)
            chars.clear()

        if punctuation > 0:  # choosing punctuation characters
            for _ in range(punctuation):
                char = random.choice(string.punctuation)
                chars.add(char)
                password.append(char)
            print("Punctuation characters chosen:", *chars)
            chars.clear()

        print("\nCharacter count: ")
        for x in set(password):  # printing counts (and if character is repeated or not) of each character
            if password.count(x) > 1:
                print(f"{x} -> {password.count(x)} (Repeated Character)")
            else:
                print(f"{x} -> {password.count(x)}")

        password.append(extra)
        random.shuffle(password)
        password = ''.join(password)  # turning password to string
        passwords.append(password)
        print(f"Password no.{p+1} -> {password}")

    print('')
    for x in range(amount):
        print(f"{x+1}. {passwords[x]}")
    return 'Thank you for using this script!'


print(password(uppercase=10, lowercase=10, digits=10, amount=5))

print("." * 2000)
