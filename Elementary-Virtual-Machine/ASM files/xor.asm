# xor function
.ORIG x0000
# R0 = A, R1 = B, R3 = A XOR B
LD R0 VAL_A
LD R1 VAL_B

# A_AND_B = A & B
AND R2 R0 R1

# A_OR_B = ~(~A & ~B)
NOT R3 R0
NOT R4 R1
AND R3 R3 R4
NOT R3 R3

# XOR = (A | B) & ~(A & B)
NOT R2 R2
AND R3 R3 R2
HALT

DATA_SECTION
VAL_A .SET 13
VAL_B .SET 7
.END
# 13 xor 7 = 10