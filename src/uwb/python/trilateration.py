
# this approach checks all three combinations of TWO anchors, i.e. (a0, a1), (a0, a2), (a1, a2) for tag distance
# then, takes the two distances that are the most similar, average them out, getting the "best" distance
# (this approach tries to mitigate any outlier tag from a bad reading)

def perform_trilateration(d0, d1, d2, anchor_coords):
    print("Performing Trilateration")
    # get anchor coordinates
    point_a0 = anchor_coords[0]
    point_a1 = anchor_coords[1]
    point_a2 = anchor_coords[2]

    # unpack tuples to extract x and y values 
    x_a0, y_a0 = point_a0
    x_a1, y_a1 = point_a1
    x_a2, y_a2 = point_a2

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

    def solve(a, b):
        try:
            sol = np.linalg.solve(a, b)
        except np.linalg.LinAlgError:
            sol = np.linalg.lstsq(a,b, rcond=None)[0]
        return sol
    
    # get 2 rows from A and same rows from B
    A_01 = A[0:2]
    B_01 = B[0:2]

    A_12 = A[1:3]
    B_12 = B[1:3]

    A_02 = A[[0, 2]]
    B_02 = B[[0, 2]]

    # get tag's estimated point from solving for two different anchors
    xt_a0a1, yt_a0a1 = solve(A_01, B_01)
    xt_a1a2, yt_a1a2 = solve(A_12, B_12)
    xt_a0a2, yt_a0a2 = solve(A_02, B_02)

    # convert solutions to np arrays
    point_a0a1 = np.array([xt_a0a1, yt_a0a1])
    point_a1a2 = np.array([xt_a1a2, yt_a1a2])
    point_a0a2 = np.array([xt_a0a2, yt_a0a2])

    # comparing the distances of each estimated location to find the closest two distances (eliminating outlier)
    estdist_01_12 = np.linalg.norm(point_a0a1 - point_a1a2)
    estdist_01_02 = np.linalg.norm(point_a0a1 - point_a0a2)
    estdist_12_02 = np.linalg.norm(point_a1a2 - point_a0a2)

    if estdist_01_12 <= estdist_01_02 and estdist_01_12 <= estdist_12_02:
        avg = (point_a0a1 + point_a1a2)/2
    elif estdist_01_02 <= estdist_01_12 and estdist_01_02 <= estdist_12_02:
        avg = (point_a0a1 + point_a0a2)/2
    else:
        avg = (point_a1a2 + point_a0a2)/2

    # return the average of the two points with the closest distance
    return avg[0], avg[1]  



# this approach uses all three anchor distances from the tag and computes a system of equations
# to find the best x and y values for the tag that fits the system 
# (may be influenced by outlier anchor values)

'''
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
'''