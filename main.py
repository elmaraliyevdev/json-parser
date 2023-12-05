import json
import sys
import re

class JSONLexer:
    def __init__(self, input_string):
        self.input_string = input_string
        self.position = 0
        self.tokens = self.tokenize()

    def tokenize(self):
        tokens = []
        while self.position < len(self.input_string):
            current_char = self.input_string[self.position]

            if current_char.isspace():
                self.position += 1
            elif current_char in ('{', '}', '[', ']', ':', ','):
                tokens.append(current_char)
                self.position += 1
            elif current_char == '"':
                # Handle strings
                start = self.position + 1
                end = self.input_string.find('"', start)
                if end == -1:
                    raise ValueError("Unterminated string")
                tokens.append(self.input_string[start:end])
                self.position = end + 1
            elif current_char.isalpha() or current_char == '_':
                # Handle unquoted keys
                start = self.position
                while self.position < len(self.input_string) and (self.input_string[self.position].isalnum() or self.input_string[self.position] == '_'):
                    self.position += 1
                tokens.append(self.input_string[start:self.position])
            else:
                # Handle numbers
                pattern = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')
                match = pattern.match(self.input_string, self.position)
                if match:
                    tokens.append(match.group())
                    self.position = match.end()
                else:
                    raise ValueError(f"Invalid token at position {self.position}")

        return tokens

class JSONParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = 0

    def get_next_token(self):
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
            self.token_index += 1
        else:
            self.current_token = None

    def parse_object(self):
        while self.current_token != "}":
            key = self.current_token.strip('"')
            self.get_next_token()  # Consume key
            if self.current_token != ":":
                self.error("Expected ':' after key")
            self.get_next_token()  # Consume ':'
            self.parse_value()  # Parse value

            if self.current_token == ",":
                self.get_next_token()  # Consume ','
            elif self.current_token != "}":
                self.error("Expected '}' or ',' in object")

        self.get_next_token()  # Consume '}'

    def parse_array(self):
        while self.current_token != "]":
            self.parse_value()  # Parse value

            if self.current_token == ",":
                self.get_next_token()  # Consume ','
            elif self.current_token != "]":
                self.error("Expected ']' or ',' in array")

        self.get_next_token()  # Consume ']'

    def parse_value(self):
        if self.current_token == "{":
            self.get_next_token()  # Consume '{'
            if self.current_token != "}":  # Check if object is not empty
                self.parse_object()
        elif self.current_token == "[":
            self.get_next_token()  # Consume '['
            if self.current_token != "]":  # Check if array is not empty
                self.parse_array()
        else:
            try:
                json.loads(self.current_token)
            except json.JSONDecodeError:
                self.error(f"Invalid JSON value: {self.current_token}")

            self.get_next_token()  # Consume value

    def error(self, message):
        print(f"Error: {message}")
        sys.exit(1)

    def parse_json(self):
        self.get_next_token()
        self.parse_value()

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

if __name__ == "__main__":
    # Step 1: Parse a valid simple JSON object
    test_json_step1 = read_json_file("test/fail1.json")
    lexer = JSONLexer(test_json_step1)
    parser = JSONParser(lexer.tokens)
    parser.parse_json()

    # Step 1: Parse an invalid JSON object
    test_json_invalid_step1 = "{"
    lexer_invalid = JSONLexer(test_json_invalid_step1)
    parser_invalid = JSONParser(lexer_invalid.tokens)
    parser_invalid.parse_json()