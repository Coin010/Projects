# left shift
.ORIG x0000
# assign values
LD R0 VAL_ADDER
LD R1 COUNT_ADDER

# skips 0 case
LSHIFT BRz FIN

# main loop
ADD R0 R0 R0
ADD R1 R1 #-1
BRp LSHIFT
FIN HALT

DATA_SECTION
VAL_ADDER .SET 2067
COUNT_ADDER .SET 1
.END
# adder value should = 4134