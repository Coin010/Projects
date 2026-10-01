# right shift (mask-based)
.ORIG x0000
# R0 = input value, R3 = shifted output
LD R0 VAL_ADDER
LD R1 MASKIN
LD R2 MASKOUT
LD R3 ZERO

# For each bit: if (R0 & MASKIN) != 0 then set MASKOUT in result.
RSHIFT_LOOP
AND R4 R0 R1
BRz NEXT_BIT
ADD R3 R3 R2

NEXT_BIT
ADD R1 R1 R1
BRz FIN
ADD R2 R2 R2
BR RSHIFT_LOOP

FIN
HALT

DATA_SECTION
VAL_ADDER .SET 2067
MASKIN .SET 2
MASKOUT .SET 1
ZERO .SET 0
.END
# MASKIN = 0010, MASKOUT = 0001
# 2067 right shifted by 1 = 1033