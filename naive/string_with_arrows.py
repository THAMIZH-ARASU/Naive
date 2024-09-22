def string_with_arrows(text, start_pos, end_pos):
    result = ''

    #Calculate indices
    index_start = max(text.rfind('\n', 0, start_pos.index), 0)
    index_end = text.find('\n', index_start + 1)
    if index_end < 0: 
        index_end = len(text)

    line_count = end_pos.line - start_pos.line + 1
    for i in range(line_count):
        #Calculate line columns
        line = text[index_start : index_end]
        column_start = start_pos.column if i == 0 else 0
        column_end = end_pos.column if i == line_count - 1 else len(line) - 1

        #append to result
        result += line + '\n'
        result += ' ' * column_start + '↑' * (column_end - column_start)

        #recalculate indices
        index_start = index_end
        index_end = text.find('\n', index_start + 1)
        if index_end < 0: index_end = len(text)
    return result.replace('\t', '')