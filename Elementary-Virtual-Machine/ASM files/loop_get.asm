# Loop program using GET opcode with labels and directives
# This program reads numbers using GET and adds them together until 0 is entered
# When 0 is entered, it outputs the sum and terminates

.ORIG x2000

# Initialize sum register to 0 (registers start at 0, so this is optional)


# Main loop - get input and process
MAIN_LOOP
GET R0
BRZ END_LOOP

# Add the input to our running sum
ADD R1 R1 R0

# Display current sum
PUT R1

# Continue the loop
BR MAIN_LOOP

# End of loop - output final result and halt
END_LOOP
PUT R1
HALT

# Data section with constants and variables
DATA_SECTION
SUM_STORAGE .SET 0   
.END
