class EOC:
    ip = '0'* 16 # instruction pointer
    # Add other components here
    memory = ['0'*16]*2**16
    r0,r1,r2,r3,r4,r5,r6,r7 = '0'*16, '0'*16 ,'0'*16, '0'*16, '0'*16, '0'*16, '0'*16, '0'*16
    ir = '0'*16 # instruction regrister
    N,P,Z = '0','0','0'
    halted = False
    # If you want to write this program as using Python Objects, that could be fun
    # however, my plan was to use a class as a way to join together the parts of
    # our virtual computer  (i.e. not including methods; just using it like struct).





class Translator:
    """Assembly instruction translator - converts opcodes to 16-bit binary strings"""
    
    def __init__(self):
        # Opcode mappings (4-bit opcodes) - matching the decode function
        self.opcodes = {
            'HALT': '0000',    # BREAK
            'ADD': '0001', 
            'AND': '0010',
            'NOT': '0011',
            'LD': '0100',
            'LDI': '0101',
            'LDR': '0110',
            'ST': '0111',
            'STI': '1000',
            'STR': '1001',
            'GET': '1010',
            'GETC': '1010',   # Same as GET
            'PUT': '1011',
            'PUTC': '1011',   # Same as PUT
            'BR': '1100',
            'BRN': '1100',    # Branch variants all use same opcode
            'BRZ': '1100',
            'BRP': '1100',
            'BRNZ': '1100',
            'BRZP': '1100',
            'BRNP': '1100',
            'BRNZP': '1100',
            'JMP': '1101',
            'JSR': '1101',
            'JMPR': '1110',    # JMPR/JSRR
            'RET': '1111'
        }
    
    def translate(self, opcode, operands):
        """Main translation method - routes to specific opcode handlers"""
        opcode_upper = opcode.upper()
        
        if opcode_upper in self.opcodes:
            # Call the appropriate translation method
            method_name = f'translate_{opcode_upper.lower()}'
            if hasattr(self, method_name):
                return getattr(self, method_name)(operands)
            else:
                return self.translate_generic(opcode_upper, operands)
        else:
            raise ValueError(f"Unknown opcode: {opcode}")
    
    def parse_register(self, reg_str):
        """Parse register string (r0-r7) to 3-bit binary"""
        if reg_str.lower().startswith('r'):
            reg_num = int(reg_str[1:])
            if 0 <= reg_num <= 7:
                return format(reg_num, '03b')
        raise ValueError(f"Invalid register: {reg_str}")
    
    def parse_immediate(self, imm_str, bits=5):
        """Parse immediate value to signed binary"""
        # Handle hex values (x prefix) or # prefix
        if imm_str.startswith('x'):
            value = int(imm_str[1:], 16)
        elif imm_str.startswith('#'):
            value = int(imm_str[1:])
        else:
            value = int(imm_str)

        min_signed = -(1 << (bits - 1))
        max_signed = (1 << (bits - 1)) - 1
        if value < min_signed or value > max_signed:
            raise ValueError(
                f"Immediate {value} out of range for {bits}-bit signed field "
                f"({min_signed} to {max_signed})"
            )
        
        # Convert to signed binary
        if value < 0:
            value = (1 << bits) + value  # Two's complement
        
        return format(value, f'0{bits}b')
    
    def parse_offset(self, offset_str, bits=9):
        """Parse offset value to signed binary"""
        return self.parse_immediate(offset_str, bits)
    
    def translate_add(self, operands):
        """ADD DR, SR1, SR2 or ADD DR, SR1, #imm5"""
        parts = operands.split()
        if len(parts) != 3:
            raise ValueError("ADD requires 3 operands")
        
        dr = self.parse_register(parts[0])
        sr1 = self.parse_register(parts[1])
        
        # Check if third operand is immediate (starts with #)
        if parts[2].startswith('#'):
            # Immediate mode
            imm5 = self.parse_immediate(parts[2], 5)
            return self.opcodes['ADD'] + dr + sr1 + '1' + imm5
        else:
            # Register mode
            sr2 = self.parse_register(parts[2])
            return self.opcodes['ADD'] + dr + sr1 + '000' + sr2
    
    def translate_and(self, operands):
        """AND DR, SR1, SR2 or AND DR, SR1, #imm5"""
        parts = operands.split()
        if len(parts) != 3:
            raise ValueError("AND requires 3 operands")
        
        dr = self.parse_register(parts[0])
        sr1 = self.parse_register(parts[1])
        
        if parts[2].startswith('#'):
            # Immediate mode
            imm5 = self.parse_immediate(parts[2], 5)
            return self.opcodes['AND'] + dr + sr1 + '1' + imm5
        else:
            # Register mode
            sr2 = self.parse_register(parts[2])
            return self.opcodes['AND'] + dr + sr1 + '000' + sr2
    
    def translate_not(self, operands):
        """NOT DR, SR"""
        parts = operands.split()
        if len(parts) != 2:
            raise ValueError("NOT requires 2 operands")
        
        dr = self.parse_register(parts[0])
        sr = self.parse_register(parts[1])
        return self.opcodes['NOT'] + dr + sr + '111111'
    
    def translate_ld(self, operands):
        """LD DR, offset9"""
        parts = operands.split()
        if len(parts) != 2:
            raise ValueError("LD requires 2 operands")
        
        dr = self.parse_register(parts[0])
        offset9 = self.parse_offset(parts[1], 9)
        return self.opcodes['LD'] + dr + offset9
    
    def translate_ldi(self, operands):
        """LDI DR, offset9"""
        parts = operands.split()
        if len(parts) != 2:
            raise ValueError("LDI requires 2 operands")
        
        dr = self.parse_register(parts[0])
        offset9 = self.parse_offset(parts[1], 9)
        return self.opcodes['LDI'] + dr + offset9
    
    def translate_ldr(self, operands):
        """LDR DR, BaseR, offset6"""
        parts = operands.split()
        if len(parts) != 3:
            raise ValueError("LDR requires 3 operands")
        
        dr = self.parse_register(parts[0])
        baser = self.parse_register(parts[1])
        offset6 = self.parse_offset(parts[2], 6)
        return self.opcodes['LDR'] + dr + baser + offset6
    
    def translate_st(self, operands):
        """ST SR, offset9"""
        parts = operands.split()
        if len(parts) != 2:
            raise ValueError("ST requires 2 operands")
        
        sr = self.parse_register(parts[0])
        offset9 = self.parse_offset(parts[1], 9)
        return self.opcodes['ST'] + sr + offset9
    
    def translate_sti(self, operands):
        """STI SR, offset9"""
        parts = operands.split()
        if len(parts) != 2:
            raise ValueError("STI requires 2 operands")
        
        sr = self.parse_register(parts[0])
        offset9 = self.parse_offset(parts[1], 9)
        return self.opcodes['STI'] + sr + offset9
    
    def translate_str(self, operands):
        """STR SR, BaseR, offset6"""
        parts = operands.split()
        if len(parts) != 3:
            raise ValueError("STR requires 3 operands")
        
        sr = self.parse_register(parts[0])
        baser = self.parse_register(parts[1])
        offset6 = self.parse_offset(parts[2], 6)
        return self.opcodes['STR'] + sr + baser + offset6
    
    def translate_br(self, operands):
        """BR offset9 or BRn/BRz/BRp/BRnz/etc variations"""
        # Handle condition codes (n, z, p)
        n = z = p = '0'
        offset_str = operands.strip()
        
        # For now, default BR sets nzp to 111 (unconditional)
        if operands.strip():
            n = z = p = '1'
            offset9 = self.parse_offset(offset_str, 9)
        else:
            raise ValueError("BR requires offset")
        
        return self.opcodes['BR'] + n + z + p + offset9
    
    def translate_brn(self, operands):
        """BRN offset9 - Branch if negative"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['BR'] + '100' + offset9  # N=1, Z=0, P=0
    
    def translate_brz(self, operands):
        """BRZ offset9 - Branch if zero"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['BR'] + '010' + offset9  # N=0, Z=1, P=0
    
    def translate_brp(self, operands):
        """BRP offset9 - Branch if positive"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['BR'] + '001' + offset9  # N=0, Z=0, P=1
    
    def translate_brnz(self, operands):
        """BRNZ offset9 - Branch if negative or zero"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['BR'] + '110' + offset9  # N=1, Z=1, P=0
    
    def translate_brzp(self, operands):
        """BRZP offset9 - Branch if zero or positive"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['BR'] + '011' + offset9  # N=0, Z=1, P=1
    
    def translate_brnp(self, operands):
        """BRNP offset9 - Branch if negative or positive"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['BR'] + '101' + offset9  # N=1, Z=0, P=1
    
    def translate_brnzp(self, operands):
        """BRNZP offset9 - Branch always (unconditional)"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['BR'] + '111' + offset9  # N=1, Z=1, P=1
    
    def translate_jmp(self, operands):
        """JMP offset9"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['JMP'] + '0' + '00' + offset9

    def translate_jsr(self, operands):
        """JSR offset9"""
        offset9 = self.parse_offset(operands.strip(), 9)
        return self.opcodes['JSR'] + '1' + '00' + offset9
    
    def translate_ret(self, operands):
        """RET (special case of JMP r7)"""
        return self.opcodes['RET'] + '000' + '111' + '000000'  # JMP R7
    
    def translate_halt(self, operands):
        """HALT (opcode 0000)"""
        return self.opcodes['HALT'] + '000000000000'  # HALT + 12 zeros
    
    def translate_get(self, operands):
        """GET DR (integer mode) or GETC DR (character mode)"""
        parts = operands.split()
        if len(parts) != 1:
            raise ValueError("GET requires 1 operand (destination register)")
        
        dr = self.parse_register(parts[0])
        # Default to integer mode (bit 7 = 0)
        return self.opcodes['GET'] + dr + '0' + '11111111'
    
    def translate_getc(self, operands):
        """GETC DR (character input mode)"""
        parts = operands.split()
        if len(parts) != 1:
            raise ValueError("GETC requires 1 operand (destination register)")
        
        dr = self.parse_register(parts[0])
        # Character mode (bit 7 = 1)
        return self.opcodes['GET'] + dr + '1' + '11111111'
    
    def translate_generic(self, opcode, operands):
        """Generic handler for unimplemented opcodes"""
        # Return opcode + zeros for now
        return self.opcodes[opcode] + '000000000000'


def clear(vc, params):
    """Clear all memory to zeros"""
    print("Clearing memory...")
    for i in range(len(vc.memory)):
        vc.memory[i] = '0'*16
    print("Memory cleared successfully")
    #There is more to this, but this is a good start

def assemble(vc, params):
    
    # Create translator class
    translator = Translator()

    try:
        parts = params.strip().split()
        if len(parts) != 1:
            print("Assemble command requires exactly one filename")
            print("Usage: ASSEMBLE filename")
            return
        fname = parts[0]  # First part (filename)
        try:
            with open(fname, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Error: File '{fname}' not found")
            return
        except Exception as e:
            print(f"Error reading file '{fname}': {e}")
            return

        # Two-pass assembler 
        symbol_table = {}  # Maps labels to addresses
        current_address = 0
        orig_address = 0
        
        directive_tokens = {'.ORIG', '.END', '.FILL', '.SET', '.ASCII', '.BLOCK'}

        def parse_set_unsigned(value_str): # directive function to parse .SET unsigned value
            """Parse .SET value as unsigned 16-bit integer."""
            value = int(value_str)
            if value < 0 or value > 0xFFFF:
                raise ValueError(f".SET value {value} out of range (0 to 65535)")
            return value

        def parse_fill_hex(value_str): # directive function to parse .FILL hex value
            """Parse .FILL value as required hex literal (xNNNN)."""
            if not value_str.startswith('x'):
                raise ValueError(f".FILL requires a hex value starting with 'x', got '{value_str}'")
            return int(value_str[1:], 16)

        def parse_ascii_text(ascii_parts): # directive function to parse .ASCII text from the line
            """Parse .ASCII text; accepts bare text or quoted text."""
            text = ' '.join(ascii_parts).strip()
            if not text:
                raise ValueError(".ASCII requires a string value")
            if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
                text = text[1:-1]
            return text

        def write_binary_with_comment(translation_file, asm_text, binary_value):
            """Write assembly comment line followed by binary value line."""
            translation_file.write(f"# {asm_text}\n")
            translation_file.write(binary_value + '\n')

        def write_ascii_data(translation_file, text, asm_text): # directive function to write ascii data to the output file
            """Write ASCII characters followed by NULL terminator."""
            for ch in text:
                write_binary_with_comment(translation_file, asm_text, format(ord(ch) & 0xFFFF, '016b'))
            write_binary_with_comment(translation_file, asm_text, '0000000000000000')

        def parse_block_count(value_str):
            """Parse .BLOCK count as non-negative integer."""
            count = int(value_str)
            if count < 0:
                raise ValueError(f".BLOCK count {count} must be non-negative")
            return count

        # FIRST PASS: Build symbol table
        print("First pass: Building symbol table...")
        for line_num, line in enumerate(lines, 1): # ex: line_num=1, line=".ORIG x0000"
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            tokens = line.split()
            if not tokens:
                continue

            first = tokens[0].upper()

            # Handle directive-only lines
            if first == '.ORIG':
                if len(tokens) < 2:
                    print(f"Missing origin value on line {line_num}")
                    continue
                hex_string = tokens[1]
                if hex_string.startswith('x'):
                    orig_address = int(hex_string[1:], 16)
                else:
                    orig_address = int(hex_string, 16)
                current_address = orig_address
                vc.ip = format(orig_address, '016b')
                print(f"  Origin set to: x{orig_address:04X}")
                continue
            if first == '.END':
                break
            if first == '.FILL':
                current_address += 1
                continue
            if first == '.SET':
                current_address += 1
                continue
            if first == '.ASCII':
                try:
                    ascii_text = parse_ascii_text(tokens[1:])
                except ValueError as e:
                    print(f"Translation error on line {line_num}: {e}")
                    return
                current_address += len(ascii_text) + 1
                continue
            if first == '.BLOCK':
                if len(tokens) < 2:
                    print(f"Translation error on line {line_num}: .BLOCK requires a count")
                    return
                try:
                    block_count = parse_block_count(tokens[1])
                except ValueError as e:
                    print(f"Translation error on line {line_num}: {e}")
                    return
                current_address += block_count
                continue

            # Standalone label line (e.g., "DATA_SECTION")
            if len(tokens) == 1 and first not in translator.opcodes:
                label = tokens[0]
                symbol_table[label] = current_address
                print(f"  Label '{label}' -> address x{current_address:04X}")
                continue

            # Handle label + directive/instruction on same line
            if len(tokens) >= 2 and first not in translator.opcodes and first not in directive_tokens:
                second = tokens[1].upper()
                if second in translator.opcodes or second in directive_tokens:
                    label = tokens[0]
                    symbol_table[label] = current_address
                    print(f"  Label '{label}' -> address x{current_address:04X}")

                    if second == '.END':
                        break
                    if second == '.ORIG':
                        if len(tokens) >= 3:
                            hex_string = tokens[2]
                            if hex_string.startswith('x'):
                                orig_address = int(hex_string[1:], 16)
                            else:
                                orig_address = int(hex_string, 16)
                            current_address = orig_address
                            vc.ip = format(orig_address, '016b')
                            print(f"  Origin set to: x{orig_address:04X}")
                        continue
                    if second == '.FILL':
                        current_address += 1
                        continue
                    if second == '.SET':
                        current_address += 1
                        continue
                    if second == '.ASCII':
                        try:
                            ascii_text = parse_ascii_text(tokens[2:])
                        except ValueError as e:
                            print(f"Translation error on line {line_num}: {e}")
                            return
                        current_address += len(ascii_text) + 1
                        continue
                    if second == '.BLOCK':
                        if len(tokens) < 3:
                            print(f"Translation error on line {line_num}: .BLOCK requires a count")
                            return
                        try:
                            block_count = parse_block_count(tokens[2])
                        except ValueError as e:
                            print(f"Translation error on line {line_num}: {e}")
                            return
                        current_address += block_count
                        continue

                    # Label + instruction
                    current_address += 1
                    continue

            # Regular instruction line
            current_address += 1

        # SECOND PASS: Generate code with label resolution
        print("\nSecond pass: Generating code...")
        current_address = orig_address
        output_fname = f"{fname.rsplit('.', 1)[0]}.eoc"
        with open(output_fname, 'w') as translation_file:
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                source_line = line
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                tokens = line.split()
                if not tokens:
                    continue

                first = tokens[0].upper()

                # Skip ORIG in pass 2
                if first == '.ORIG':
                    continue

                # END/.END writes halt sentinel then stops output
                if first == '.END':
                    end_binary = '0000000000000000'
                    print("\tEND")
                    print(f"Binary: {end_binary}")
                    write_binary_with_comment(translation_file, source_line, end_binary)
                    break

                # .FILL/FILL directive without label
                if first == '.FILL':
                    if len(tokens) < 2:
                        print(f"Translation error on line {line_num}: .FILL requires a value")
                        return
                    fill_value = tokens[1]
                    try:
                        value = parse_fill_hex(fill_value)
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    binary_value = format(value & 0xFFFF, '016b')
                    print(f"\t.FILL\t{fill_value}")
                    print(f"Binary: {binary_value}")
                    write_binary_with_comment(translation_file, source_line, binary_value)
                    current_address += 1
                    continue
                if first == '.SET':
                    if len(tokens) < 2:
                        print(f"Translation error on line {line_num}: .SET requires an unsigned integer value")
                        return
                    try:
                        value = parse_set_unsigned(tokens[1])
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    binary_value = format(value, '016b')
                    print(f"\t.SET\t{tokens[1]}")
                    print(f"Binary: {binary_value}")
                    write_binary_with_comment(translation_file, source_line, binary_value)
                    current_address += 1
                    continue
                if first == '.ASCII':
                    try:
                        ascii_text = parse_ascii_text(tokens[1:])
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    print(f"\t.ASCII\t{ascii_text}")
                    for ch in ascii_text:
                        print(f"Binary: {format(ord(ch) & 0xFFFF, '016b')}")
                    print("Binary: 0000000000000000")
                    write_ascii_data(translation_file, ascii_text, source_line)
                    current_address += len(ascii_text) + 1
                    continue
                if first == '.BLOCK':
                    if len(tokens) < 2:
                        print(f"Translation error on line {line_num}: .BLOCK requires a count")
                        return
                    try:
                        block_count = parse_block_count(tokens[1])
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    print(f"\t.BLOCK\t{tokens[1]}")
                    for i in range(block_count):
                        print("Binary: 0000000000000000")
                        write_binary_with_comment(translation_file, source_line, '0000000000000000')
                    current_address += block_count
                    continue

                # Remove label prefix for "label + directive/instruction" lines
                if len(tokens) >= 2 and first not in translator.opcodes and first not in directive_tokens:
                    second = tokens[1].upper()
                    if second in translator.opcodes or second in directive_tokens:
                        tokens = tokens[1:]
                        first = tokens[0].upper()

                # Standalone label line
                if len(tokens) == 1 and first not in translator.opcodes and first not in directive_tokens:
                    continue

                # Handle directives after stripping label
                if first == '.ORIG':
                    continue
                if first == '.END':
                    end_binary = '0000000000000000'
                    print("\tEND")
                    print(f"Binary: {end_binary}")
                    write_binary_with_comment(translation_file, source_line, end_binary)
                    break
                if first == '.FILL':
                    if len(tokens) < 2:
                        print(f"Translation error on line {line_num}: .FILL requires a value")
                        return
                    fill_value = tokens[1]
                    try:
                        value = parse_fill_hex(fill_value)
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    binary_value = format(value & 0xFFFF, '016b')
                    print(f"\t.FILL\t{fill_value}")
                    print(f"Binary: {binary_value}")
                    write_binary_with_comment(translation_file, source_line, binary_value)
                    current_address += 1
                    continue
                if first == '.SET':
                    if len(tokens) < 2:
                        print(f"Translation error on line {line_num}: .SET requires an unsigned integer value")
                        return
                    try:
                        value = parse_set_unsigned(tokens[1])
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    binary_value = format(value, '016b')
                    print(f"\t.SET\t{tokens[1]}")
                    print(f"Binary: {binary_value}")
                    write_binary_with_comment(translation_file, source_line, binary_value)
                    current_address += 1
                    continue
                if first == '.ASCII':
                    try:
                        ascii_text = parse_ascii_text(tokens[1:])
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    print(f"\t.ASCII\t{ascii_text}")
                    for ch in ascii_text:
                        print(f"Binary: {format(ord(ch) & 0xFFFF, '016b')}")
                    print("Binary: 0000000000000000")
                    write_ascii_data(translation_file, ascii_text, source_line)
                    current_address += len(ascii_text) + 1
                    continue
                if first == '.BLOCK':
                    if len(tokens) < 2:
                        print(f"Translation error on line {line_num}: .BLOCK requires a count")
                        return
                    try:
                        block_count = parse_block_count(tokens[1])
                    except ValueError as e:
                        print(f"Translation error on line {line_num}: {e}")
                        print(f"Line: {line}")
                        return

                    print(f"\t.BLOCK\t{tokens[1]}")
                    for i in range(block_count):
                        print("Binary: 0000000000000000")
                        write_binary_with_comment(translation_file, source_line, '0000000000000000')
                    current_address += block_count
                    continue
                
                if not tokens: # safely skips problematic lines instead of crashing the assembler (if tokens doesn't get filled)
                    print("Skipping malformed line")
                    continue
                
                try:
                    if len(tokens) >= 1:
                        opcode = tokens[0].upper()
                        operands = ' '.join(tokens[1:]) if len(tokens) > 1 else ""
                        
                        # Replace labels in operands with addresses
                        if operands: # oppertands to work with
                            operand_tokens = operands.split()
                            resolved_operands = []
                            
                            for token in operand_tokens:
                                # Check if token is a label reference
                                if token in symbol_table: # check if token exists as a key in the symbol table
                                    # Calculate offset for relative addressing (like BR, LD, ST)
                                    if opcode in ['BR', 'BRN', 'BRZ', 'BRP', 'BRNZ', 'BRZP', 'BRNP', 'BRNZP', 'LD', 'ST', 'LDI', 'STI', 'JMP', 'JSR']:
                                        # Use PC-relative offset (target_address - (current_address + 1))
                                        offset = symbol_table[token] - (current_address + 1)
                                        # Keep signed offset; parse_immediate will range-check and encode it.
                                        resolved_operands.append(f"#{offset}")
                                    else:
                                        # For other instructions, use absolute address
                                        resolved_operands.append(f"x{symbol_table[token]:04X}")
                                    print(f"    Resolved label '{token}' -> x{symbol_table[token]:04X}")
                                else:
                                    resolved_operands.append(token)
                            
                            operands = ' '.join(resolved_operands)
                        
                        # Translate to binary
                        binary_instruction = translator.translate(opcode, operands)
                        
                        # Output formatted result
                        formatted_output = f"\t{opcode}\t{operands}" if operands else f"\t{opcode}\t"
                        print(formatted_output)
                        print(f"Binary: {binary_instruction}")
                        write_binary_with_comment(translation_file, source_line, binary_instruction)
                        current_address += 1
                        
                except ValueError as e:
                    print(f"Translation error on line {line_num}: {e}")
                    print(f"Line: {line}")
                    return

        print(f"Translation output written to '{output_fname}'")
                    
    except Exception as e:
        print(f"Error in ASSEMBLE command: {e}")    
def aload(vc,params):
    """Load a program file into memory"""
    try:
        parts = params.strip().split()
        if len(parts) != 1:
            print("assembler load only requires filename")
            print("Usage: aload filename")
            return
        fname = parts[0]
        try:
            with open(fname, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Error: File '{fname}' not found")
            return
        except Exception as e:
            print(f"Error reading file '{fname}': {e}")
            return

        current_addr = int(vc.ip, 2)
        instructions_loaded = 0
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('.'):  # Skip empty lines and comments and directives
                # Ensure instruction is 16 bits
                if len(line) == 16 and all(c in '01' for c in line):
                    if current_addr < len(vc.memory):
                        vc.memory[current_addr] = line
                        current_addr += 1
                        instructions_loaded += 1
                    else:
                        print(f"Warning: Memory overflow at address {current_addr}")
                        break
                else:
                    print(f"Warning: Invalid instruction format: '{line}' (must be 16-bit binary)")

        print(f"Successfully loaded {instructions_loaded} instructions from '{fname}'")
        print(f"Starting address: {current_addr - instructions_loaded} (binary: {format(current_addr - instructions_loaded, '016b')})")
        print(f"Instruction pointer remains at: {vc.ip}")
    except Exception as e:
        print(f"Error in ALOAD command: {e}")



def load(vc, params):
    """Load a program file into memory at specified address"""
    try:
        # Parse parameters: "fname addr"
        parts = params.strip().split()
        if len(parts) != 2:
            print("Error: LOAD command requires filename and address")
            print("Usage: LOAD filename address")
            return
        
        fname, addr_str = parts



        
        
        # Convert address from binary string to integer
        try:
            addr = int(addr_str, 2)  # Assuming address is in binary format
        except ValueError:
            try:
                addr = int(addr_str, 16)  # Try hexadecimal
            except ValueError:
                addr = int(addr_str)  # Try decimal
        
        # Check if address is valid
        if addr < 0 or addr >= len(vc.memory):
            print(f"Error: Address {addr} is out of memory range (0 to {len(vc.memory)-1})")
            return
        
        # Read the program file
        try:
            with open(fname, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Error: File '{fname}' not found")
            return
        except Exception as e:
            print(f"Error reading file '{fname}': {e}")
            return
        
        # Load instructions into memory
        current_addr = addr
        instructions_loaded = 0
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                # Ensure instruction is 16 bits
                if len(line) == 16 and all(c in '01' for c in line):
                    if current_addr < len(vc.memory):
                        vc.memory[current_addr] = line
                        current_addr += 1
                        instructions_loaded += 1
                    else:
                        print(f"Warning: Memory overflow at address {current_addr}")
                        break
                else:
                    print(f"Warning: Invalid instruction format: '{line}' (must be 16-bit binary)")
        
        # Reset instruction pointer to the starting address
        vc.ip = format(addr, '016b')  # Convert to 16-bit binary string
        
        print(f"Successfully loaded {instructions_loaded} instructions from '{fname}'")
        print(f"Starting address: {addr} (binary: {vc.ip})")
        print(f"Instruction pointer reset to: {vc.ip}")
        
    except Exception as e:
        print(f"Error in LOAD command: {e}")

def dump(vc, params):
    """Dumping current page"""
    try:
        parts = params.strip().split()
        if len(parts) != 0:
            print("Error: DUMP command requires only the command")
            print("Usage: DUMP")
            return
        
        current = int(vc.ip, 2) # get integer adress of instruction pointer
        page_end = 2**9 + current # set the end of the dump
        while current <= page_end:
            memory_addr_format = format(int(vc.memory[current],2),'04x') # convert to int then to hex
            print(f"{memory_addr_format}: {vc.memory[current]}")
            current += 1
    except Exception as e:
        print(f"Error in DUMP command: {e}")
def regristers(vc,params):
    """Display the contents of the general purpose registers as 4-bit chunks"""
    try:
        parts = params.strip().split()
        if len(parts) != 0:
            print("Error: REGRISTERS command requires only the command")
            print("Usage: REGRISTERS")
            return
        
        for i in range(0,8):
            regrister_name = f"r{i}"
            regristar_value = getattr(vc, regrister_name)
            regrister_format = f"{regrister_name}: {regristar_value[0:4]} {regristar_value[4:8]} {regristar_value[8:12]} {regristar_value[12:]}"
            print(regrister_format)
    except Exception as e:
        print(f"Error in DUMP command: {e}")
def state(vc,params):
    """Display STATE"""
    try:
        parts = params.strip().split()
        if len(parts) != 0:
            print("Error: STATE command requires only the command")
            print("Usage: STATE")
            return
        # dump ------------------------------------------------------
        current = int(vc.ip, 2) # get integer adress of instruction pointer
        page_end = 2**9 + current # set the end of the dump
        while current <= page_end:
            memory_addr_format = format(int(vc.memory[current],2),'04x') # convert to int then to hex
            print(f"{vc.N} {vc.Z} {vc.P} instruction pointer: {vc.ip} instruction regrister: {vc.ir} {memory_addr_format}: {vc.memory[current]}")
            current += 1
        # regristers ----------------------------------------------------
        for i in range(0,8):
            regrister_name = f"r{i}"
            regristar_value = getattr(vc, regrister_name)
            regrister_format = f"{regrister_name}: {regristar_value[0:4]} {regristar_value[4:8]} {regristar_value[8:12]} {regristar_value[12:]}"
            print(f"{vc.N} {vc.Z} {vc.P} instruction pointer: {vc.ip} instruction regrister: {vc.ir} {regrister_format}")
    except Exception as e:
        print(f"Error in STATE command: {e}")
def run(vc,params):
    
    try:
        parts = params.strip().split()
        if len(parts) != 0:
            print("Error: RUN command requires only the command")
            print("Usage: RUN")
            return
        vc.halted = False
        while not vc.halted:
            vc.ir = vc.ip
            # Convert binary string to integer, add 1, convert back to 16-bit binary
            vc.ip = format(int(vc.ip, 2) + 1, '016b') # increments ip by 1
            loc_in_memory = vc.memory[int(vc.ir,2)] # convert ir to int then map to loc in memory
            #print(loc_in_memory)
            decode(vc,loc_in_memory)

    except Exception as e:
        print(f"Error in RUN command: {e}")
def decode(vc,params):
    try:
        parts = params.strip().split()
        if len(parts) != 1:
            print("Error: DECODE command requires a single string of a 16 bit binary number")
            print("Usage: DECODE <string>")
            return
        part = parts[0]
        opcode = part[0:4]

        oppcode_functions = {
            '0000': BREAK,
            '0001': ADD,
            '0010': AND,
            '0011': NOT,
            '0100': LD,
            '0101': LDI,
            '0110': LDR,
            '0111': ST,
            '1000': STI,
            '1001': STR,
            '1010': GET,
            '1011': PUT,
            '1100': BR,
            '1101': JMP,
            '1110': JMPR,
            '1111': RET,
        }

        handler = oppcode_functions.get(opcode)
        if handler:
            handler(vc, part)
        else:
            print(f"Unknown opcode: {opcode}")
 
        
    except Exception as e:
        print(f"Error in DECODE command: {e}")


def BREAK(vc,params):
    # '0000' 0000 0000 0000
    vc.halted = True
    print("HALT")


def ADD(vc,params):
    # '0001' DR SR1 [0,1] [00 SR2, imm5]
    part = params
    DR = int(part[4:7],2)
    SR1 = int(part[7:10],2)
    vcDR = f"r{DR}"
    vcSR1 = f"r{SR1}"
    if (part[10] == '0'):
        # ADD with SR2
        SR2 = int(part[13:],2)
        vcSR2 = f"r{SR2}"

        value1 = int(getattr(vc, vcSR1), 2)
        value2 = int(getattr(vc, vcSR2), 2)

        # negative when sign is 1
        if (getattr(vc, vcSR1)[0] == '1'):
            value1 = signed(bin = getattr(vc,vcSR1), bits = 16)

        if (getattr(vc, vcSR2)[0] == '1'):
            value2 = signed(bin = getattr(vc,vcSR2), bits = 16)

        result = value1 + value2
        result_16bit = result & 0xFFFF  # Mask to 16 bits
        setattr(vc, vcDR, format(result_16bit, '016b'))
        
        # Set condition codes based on result
        set_condition_codes(vc, result_16bit)
        
        print(f"ADD D{vcDR} S1-{vcSR1} 0 00 S2-{vcSR2}")
    else:
        # ADD with imm5 (2's complement with sign extension)
        imm5 = part[11:] 
        
        imm5_val = int(imm5, 2)
        if imm5[0] == '1':  # Negative number (MSB is 1)
            imm5_val = signed(bin = imm5, bits = 5)
        
        # Get source register value and handle as signed if negative
        sr1_value = int(getattr(vc, vcSR1), 2)
        if getattr(vc, vcSR1)[0] == '1':
            sr1_value = signed(bin = getattr(vc, vcSR1), bits = 16)
        
        # addition result
        result = sr1_value + imm5_val
        
        # Store result as 16-bit binary (with proper overflow handling)
        result_16bit = result & 0xFFFF
        setattr(vc, vcDR, format(result_16bit, '016b'))
        
        # Set condition codes based on result
        set_condition_codes(vc, result_16bit)
        
        print(f"ADD D{vcDR} S{vcSR1} 1 imm5-{imm5_val}")

def signed(bin,bits):
    big = -1 * (2**(bits-1)) 
    otherBits = int(bin[1:],2)
    return big + otherBits

def signed_binary_value(bit_string):
    """Convert a binary string in two's complement form to a signed integer."""
    if bit_string[0] == '1':
        return signed(bit_string, len(bit_string))
    return int(bit_string, 2)

def set_condition_codes(vc, value):
    """Set condition codes N, Z, P based on a 16-bit result value"""
    # Ensure value is within 16-bit range
    value = value & 0xFFFF
    
    if value == 0:
        # Zero
        vc.N, vc.Z, vc.P = '0', '1', '0'
    elif value & 0x8000:  # Check MSB (bit 15) for negative
        # Negative (MSB = 1)
        vc.N, vc.Z, vc.P = '1', '0', '0'
    else:
        # Positive (value > 0 and MSB = 0)
        vc.N, vc.Z, vc.P = '0', '0', '1'
def AND(vc,params):
    # '0010' DR SR1 [0,1] [00 SR2, imm5]
    part = params 
    DR = int(part[4:7],2)
    SR1 = int(part[7:10],2)
    vcDR = f"r{DR}"
    vcSR1 = f"r{SR1}"

    if (part[10] == '0'):
        # AND with SR2
        SR2 = int(part[13:],2)
        vcSR2 = f"r{SR2}"

        value1 = int(getattr(vc, vcSR1), 2)
        value2 = int(getattr(vc, vcSR2), 2)

        # Perform bitwise AND
        result = value1 & value2
        setattr(vc, vcDR, format(result, '016b'))
        
        # Set condition codes based on result
        set_condition_codes(vc, result)
        
        print(f"AND D{vcDR} S1-{vcSR1} 0 00 S2-{vcSR2}")
    else:
        # AND with imm5
        imm5 = part[11:]
        
        imm5_val = int(imm5, 2)
        if imm5[0] == '1':  # Negative number (MSB is 1) - sign extend
            imm5_val = signed(bin = imm5, bits = 5)
        
        value1 = int(getattr(vc, vcSR1), 2)
        # Perform bitwise AND with sign-extended immediate
        result = value1 & (imm5_val & 0xFFFF)  # Mask to 16 bits
        
        setattr(vc, vcDR, format(result, '016b'))
        
        # Set condition codes based on result
        set_condition_codes(vc, result)
        
        print(f"AND D{vcDR} S{vcSR1} 1 imm5-{imm5_val}")
def NOT(vc,params):
    # '0011' DR SR1 111111
    part = params
    DR = int(part[4:7], 2)
    SR1 = int(part[7:10], 2)
    vcDR = f"r{DR}"
    vcSR1 = f"r{SR1}"
    
    # Perform bitwise NOT operation
    value = int(getattr(vc, vcSR1), 2)
    result = (~value) & 0xFFFF  # Bitwise NOT and mask to 16 bits
    
    setattr(vc, vcDR, format(result, '016b'))
    
    # Set condition codes based on result
    set_condition_codes(vc, result)
    
    print(f"NOT D{vcDR} SR1-{vcSR1} 111111")


def LD(vc,params):
    # '0100' DR offset9
    part = params
    DR = int(part[4:7],2)
    vcDR = f"r{DR}"
    OFFSET9 = part[7:]
    location = (int(vc.ip, 2) + signed_binary_value(OFFSET9)) & 0xFFFF

    setattr(vc, vcDR, vc.memory[location])
    
    # Set condition codes based on loaded value
    loaded_value = int(vc.memory[location], 2)
    set_condition_codes(vc, loaded_value)
    
    print(f"LD D{DR} offset9-{OFFSET9}")

def LDI(vc,params):
    # '0101' DR offset9
    part = params
    DR = int(part[4:7],2)
    vcDR = f"r{DR}"
    OFFSET9 = part[7:]
    location = (int(vc.ip, 2) + signed_binary_value(OFFSET9)) & 0xFFFF
    location_pointer = vc.memory[location]

    setattr(vc, vcDR, vc.memory[int(location_pointer,2)])
    
    # Set condition codes based on loaded value
    loaded_value = int(vc.memory[int(location_pointer,2)], 2)
    set_condition_codes(vc, loaded_value)
    
    print(f"LDI D{DR} offset9-{OFFSET9}")

def LDR(vc,params):
    # '0110' DR baseR index6
    part = params

    DR = int(part[4:7],2)
    vcDR = f"r{DR}"
    BASER = int(part[7:10],2)
    vcBASER = f"r{BASER}"
    INDEX6 = part[10:]
    location = (int(getattr(vc, vcBASER), 2) + signed_binary_value(INDEX6)) & 0xFFFF

    setattr(vc, vcDR, vc.memory[location])

    # Set condition codes based on loaded value
    loaded_value = int(vc.memory[location], 2)
    set_condition_codes(vc, loaded_value)

    print(f"LDR D{DR} baseR{BASER} index6-{INDEX6}")
def ST(vc,params):
    # '0111' SR offset9
    part = params
    SR = int(part[4:7],2)
    vcSR = f"r{SR}"
    OFFSET9 = part[7:]
    location = (int(vc.ip, 2) + signed_binary_value(OFFSET9)) & 0xFFFF

    vc.memory[location] = getattr(vc, vcSR)
    print(f"ST SR-{int(part[4:7],2)} offset9-{OFFSET9}")

def STI(vc,params):
    # '1000' SR offset9
    part = params
    SR = int(part[4:7],2)
    vcSR = f"r{SR}"
    OFFSET9 = part[7:]
    location = (int(vc.ip, 2) + signed_binary_value(OFFSET9)) & 0xFFFF
    location_pointer = vc.memory[location]

    vc.memory[int(location_pointer,2)] = getattr(vc, vcSR)
    print(f"STI SR-{int(part[4:7],2)} offset9-{OFFSET9}")

def STR(vc,params):
    # '1001' SR baseR index6
    part = params
    SR = int(part[4:7],2)
    vcSR = f"r{SR}"
    BASER = int(part[7:10],2)
    vcBASER = f"r{BASER}"
    INDEX6 = part[10:]
    location = (int(getattr(vc, vcBASER), 2) + signed_binary_value(INDEX6)) & 0xFFFF

    vc.memory[location] = getattr(vc, vcSR)
    print(f"STR SR-{int(part[4:7],2)} baseR{int(part[7:10],2)} index6-{part[10:]}")

def GET(vc,params):
    # '1010' DR [0,1] 1111 1111
    # Bit 7 determines mode: 0 = integer input, 1 = character input
    part = params
    DR = int(part[4:7], 2)  # Extract destination register (bits 4-6)
    vcDR = f"r{DR}"
    mode = part[7]  # Bit 7: 0=integer, 1=character
    
    try:
        if mode == '0':
            # GET: Integer input mode
            print(f"GET DR{DR} (integer mode)")
            user_input = input("Enter an integer: ")
            try:
                # Convert input to integer, then to 16-bit binary
                input_value = int(user_input)
                # Handle negative numbers using 2's complement representation
                if input_value < 0:
                    input_value = (1 << 16) + input_value  # Convert to 16-bit 2's complement
                # Mask to 16 bits to handle overflow
                input_value = input_value & 0xFFFF
                binary_value = format(input_value, '016b')
                setattr(vc, vcDR, binary_value)
                
                # Set condition codes based on loaded value
                set_condition_codes(vc, input_value)
                
                print(f"Stored integer {int(user_input)} as {binary_value} in {vcDR}")
            except ValueError:
                print(f"Error: '{user_input}' is not a valid integer")
                # Store 0 on error
                setattr(vc, vcDR, '0000000000000000')
                set_condition_codes(vc, 0)
        else:
            # GETC: Character input mode  
            print(f"GETC DR{DR} (character mode)")
            user_input = input("Enter a character: ")
            if len(user_input) > 0:
                # Get ASCII value of first character and convert to 16-bit binary
                char_value = ord(user_input[0])
                binary_value = format(char_value, '016b')
                setattr(vc, vcDR, binary_value)
                
                # Set condition codes based on loaded value
                set_condition_codes(vc, char_value)
                
                print(f"Stored character '{user_input[0]}' (ASCII {char_value}) as {binary_value} in {vcDR}")
            else:
                print("Error: No character entered")
                # Store 0 on error
                setattr(vc, vcDR, '0000000000000000')
                set_condition_codes(vc, 0)
    except Exception as e:
        print(f"Error in GET instruction: {e}")
        setattr(vc, vcDR, '0000000000000000')
        set_condition_codes(vc, 0)
def PUT(vc,params):
    # '1011' SR [0,1] 1111 1111
    # Bit 7 determines mode: 0 = display as integer, 1 = display as character
    part = params
    SR = int(part[4:7], 2)  # Extract source register (bits 4-6)
    vcSR = f"r{SR}"
    mode = part[7]  # Bit 7: 0=integer, 1=character
    
    try:
        # Get the value stored in the source register
        register_value = getattr(vc, vcSR)
        
        if mode == '0':
            # PUT: Display as integer
            # Convert binary string to integer
            int_value = int(register_value, 2)
            
            # Check if it's a negative number (MSB = 1) and convert from 2's complement
            if register_value[0] == '1':
                int_value = signed(bin=register_value, bits=16)
            
            print(f"PUT: {int_value}")
            print(f"PUT SR{SR} (integer mode) - displayed: {int_value}")
            
        else:
            # PUTC: Display as character
            # Convert binary string to integer, then to ASCII character
            char_value = int(register_value, 2)
            
            # Mask to 8 bits for valid ASCII range
            char_value = char_value & 0xFF
            
            if 32 <= char_value <= 126:  # Printable ASCII range
                char = chr(char_value)
                print(f"PUTC: {char}")
                print(f"PUTC SR{SR} (character mode) - displayed: '{char}' (ASCII {char_value})")
            else:
                # Handle non-printable characters
                print(f"PUTC: [non-printable ASCII {char_value}]")
                print(f"PUTC SR{SR} (character mode) - displayed: [non-printable ASCII {char_value}]")
                
    except Exception as e:
        print(f"Error in PUT instruction: {e}")
def BR(vc,params):
    # '1100' n z p offset9
    # Branch if (n AND N) or (z AND Z) or (p AND P)
    part = params
    
    # Extract condition bits from instruction
    n_bit = part[4]  # n condition bit
    z_bit = part[5]  # z condition bit  
    p_bit = part[6]  # p condition bit
    offset9 = part[7:]  # 9-bit offset
    
    # Check condition: (n AND N) OR (z AND Z) OR (p AND P)
    branch_condition = False
    
    if (n_bit == '1' and vc.N == '1'):  # n AND N
        branch_condition = True
    if (z_bit == '1' and vc.Z == '1'):  # z AND Z  
        branch_condition = True
    if (p_bit == '1' and vc.P == '1'):  # p AND P
        branch_condition = True
    
    # Debug output showing which conditions are set
    conditions = []
    if n_bit == '1': conditions.append('n')
    if z_bit == '1': conditions.append('z') 
    if p_bit == '1': conditions.append('p')
    condition_str = ''.join(conditions) if conditions else 'unconditional'
    
    if branch_condition:
        new_location = format((int(vc.ip, 2) + signed_binary_value(offset9)) & 0xFFFF, '016b')
        
        # Update instruction pointer
        vc.ip = new_location
        
        print(f"BR {condition_str} offset9-{offset9} - BRANCH TAKEN to {new_location}")
    else:
        print(f"BR {condition_str} offset9-{offset9} - branch not taken (N={vc.N}, Z={vc.Z}, P={vc.P})")
def JMP(vc,params):
    # '1101' L 000 offset9
    # L=0: JMP - adjust instruction pointer to offset on same page
    # L=1: JSR - copy instruction pointer to R7 and adjust to offset on same page
    part = params
    L_bit = part[4]  # L bit determines JMP vs JSR
    offset9 = part[7:]  # 9-bit offset
    
    if L_bit == '0':
        new_location = format((int(vc.ip, 2) + signed_binary_value(offset9)) & 0xFFFF, '016b')
        
        vc.ip = new_location
        print(f"JMP offset9-{offset9} - jumped to {new_location}")
        
    else:
        # JSR: Save current IP to R7, then jump to offset on current page
        # Save current instruction pointer to R7
        vc.r7 = vc.ip
        
        new_location = format((int(vc.ip, 2) + signed_binary_value(offset9)) & 0xFFFF, '016b')
        
        vc.ip = new_location
        print(f"JSR offset9-{offset9} - saved IP {vc.r7} to R7, jumped to {new_location}")
def JMPR(vc,params):
    part = params
    if part[4] == '0':
        print(f"JMPR {part[4:7]} baseR{int(part[7:10],2)} index6-{part[10:]}")
    else:
        print(f"JSRR {part[4:7]} baseR{int(part[7:10],2)} index6-{part[10:]}")
def RET(vc,params):
    # '1111' - Return from subroutine
    # Restore instruction pointer from R7 (set by JSR)
    vc.ip = vc.r7
    print(f"RET - returned to IP {vc.ip} from R7")
def main():
    vc = EOC()
    print(vc.ip)   # just to show you can.

    #Setup additional Commands
    commands = {
        "CLEAR":clear,
        "LOAD":load,
        "ALOAD":aload,
        "DUMP":dump,
        "REGRISTERS":regristers,
        "STATE":state,
        "RUN":run,
        "ASSEMBLE":assemble
        }

    #This is how you invoke a command
    commands["CLEAR"](vc, "")

    # Command loop
    print("EOC Virtual Machine")
    print("Available commands: CLEAR, LOAD, ALOAD, DUMP, REGRISTERS, STATE, RUN, ASSEMBLE, QUIT")
    print("Type 'HELP' for help or 'QUIT' to exit")
    
    while True:
        try:
            user_input = input("EOC> ").strip()
            
            if not user_input:
                continue
            
            # Parse command and parameters
            parts = user_input.split(maxsplit=1)
            command = parts[0].upper()
            params = parts[1] if len(parts) > 1 else ""
            
            if command == "QUIT" or command == "EXIT":
                print("Goodbye!")
                break
            elif command == "HELP":
                print("Available commands:")
                print("  CLEAR - Clear all memory")
                print("  LOAD filename address - Load program file into memory")
                print("  ALOAD filename - Load assembled program file into memory")
                print("  DUMP - Dump current memory page")
                print("  REGRISTERS - Show register values")
                print("  STATE - Show machine state")
                print("  RUN - Run the program")
                print("  ASSEMBLE filename - Assemble source file")
                print("  QUIT - Exit the virtual machine")
            elif command in commands:
                commands[command](vc, params)
            else:
                print(f"Unknown command: {command}")
                print("Type 'HELP' for available commands")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
