import random

def build_board(n):
    return(["r"] + ["." * k for k in range(2, n)] + ["g" + "." * (n - 2) + "b"])

def random_triangle(n):
    l = []
    for row_no in range(n):
        row_len = row_no + 1
        if row_no == 0:
            row = "r"
        elif row_no == n - 1:
            row = "g" + "".join([random.choice(["g", "b"]) for k in range(row_len-2)]) + "b"
        else: 
            row = random.choice(["r", "g"]) + "".join([random.choice(["r", "b", "g"]) for k in range(row_len-2)]) + random.choice(["r", "b"])
        l.append(row)
    return(l)