def update_config(input_file, overrides, output_file):
    with open(input_file, 'r') as f:
        input_lines = f.readlines()

    with open(output_file, 'w') as o:
        for line in input_lines:
            for token in overrides:
                wildcard = "${}".format(token)
                line = line.replace(wildcard, str(overrides[token]))
        o.write(line)