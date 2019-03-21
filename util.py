def get_substring_between_parentheses(message):
    return message[message.find("(") + 1:message.find(")")]
