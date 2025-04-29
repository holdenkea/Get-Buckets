

def perform_trilateration(d0, d1, d2, anchor_coords):
    # for a complete breakdown of this algorithm and visuals see the readme on my github
    print("Performing Trilateration")
    # get coordinates
    point_a0 = anchor_coords[0]
    point_a1 = anchor_coords[1]
    point_a2 = anchor_coords[2]

    # unpack tuples to extract x and y values and
    x_a0, y_a0 = point_a0
    x_a1, y_a1 = point_a1
    x_a2, y_a2 = point_a2

    # perform matrix multiplication to generate the three equations
    # A * [xt yt] = B

    # left hand side of equation's coefficients (Matrix A)
    A = np.array([
        [x_a0 - x_a1, y_a0 - y_a1],
        [x_a1 - x_a2, y_a1 - y_a2],
        [x_a0 - x_a2, y_a0 - y_a2]
    ])

    # right hand side of equation's constants
    # square the distances
    d0_sq = d0**2
    d1_sq = d1**2
    d2_sq = d2**2

    # square the anchor coordinates
    x_a0_sq, y_a0_sq = x_a0**2, y_a0**2 
    x_a1_sq, y_a1_sq = x_a1**2, y_a1**2
    x_a2_sq, y_a2_sq = x_a2**2, y_a2**2

    rhs_0_minus_1 = -0.5 * (d0_sq - d1_sq - (x_a0_sq + y_a0_sq - x_a1_sq - y_a1_sq))
    rhs_1_minus_2 = -0.5 * (d1_sq - d2_sq - (x_a1_sq + y_a1_sq - x_a2_sq - y_a2_sq))
    rhs_0_minus_2 = -0.5 * (d0_sq - d2_sq - (x_a0_sq + y_a0_sq - x_a2_sq - y_a2_sq))

    # right hand side of equation's constants (Matrix B)
    B = np.array([
        rhs_0_minus_1, 
        rhs_1_minus_2, 
        rhs_0_minus_2
    ])

    # the system we want to solve is now A * [xt yt] = B
    # we will use np.linalg.lstsq to get the best fitting xt and yt as possible for the system, 
    xt, yt = np.linalg.lstsq(A, B, rcond=None)[0]

    return xt, yt    