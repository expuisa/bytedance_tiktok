class LZWCompressor:
    def __init__(self):
        self.current_bit_index  = 0
        self.buffer             = 0
        self.output_bytes       = []
        self.codebook           = {chr(a): a for a in range(256)}
        self.bit_length         = 8
        self.next_code          = 255

    def write(self, code, code_length):
        while code_length > 0:
            if code & 1:
                self.buffer |= 1 << self.current_bit_index
            code >>= 1
            self.current_bit_index += 1
            if self.current_bit_index == 8:
                self.output_bytes.append(self.buffer)
                self.current_bit_index = 0
                self.buffer = 0
                
            code_length -= 1

    def compress(self, data) -> list:
        index = 0
        while index < len(data):
            chunk = data[index]
            while index + 1 < len(data) and chunk + data[index + 1] in self.codebook:
                index += 1
                chunk += data[index]

            self.write(self.codebook[chunk], self.bit_length)
            if index + 1 == len(data):
                break

            self.next_code += 1

            if self.next_code & (self.next_code - 1) == 0:
                self.bit_length += 1

            self.codebook[chunk + data[index + 1]] = self.next_code
            index += 1
            
        if self.current_bit_index > 0:
            self.output_bytes.append(self.buffer)

        return self.output_bytes