# Here is a simple program to convert a letter to uppercase
# Remember that uppercase and lowercase letters are
# separated by a value of 32

.ORIG x0000
GETC R0
LD R1 MASK
AND R0 R0 R1
PUTC R0
HALT
# xFFDF is 1111 1111 1101 1111
# This masks the bit 32
# a = 97 -32 ks = 65 = A
MASK .FILL xFFDF
.END