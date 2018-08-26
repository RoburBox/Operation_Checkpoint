class BadCLIArgument(Exception):
    def __init__(self, message):
        self.message = message

def assert_date_format(date_string):
    try:
        int(date_string[0])
        int(date_string[1])
        int(date_string[2])
        int(date_string[3])
        int(date_string[5])
        int(date_string[6])
        int(date_string[8])
        int(date_string[9])
        int(date_string[11])
        int(date_string[12])
        int(date_string[14])
        int(date_string[15])
        int(date_string[17])
        int(date_string[18])
        int(date_string[20])
        int(date_string[21])
        int(date_string[22])
        int(date_string[23])
    except ValueError:
        raise BadCLIArgument('Date expects integer')
    
    if date_string[4] != '-' or date_string[7] != '-':
        raise BadCLIArgument('Date expects -')
    if date_string[10] != 'T':
        raise BadCLIArgument('Date expects T')
    if date_string[13] != '_' or date_string[16] != '_':
        raise BadCLIArgument('Date expects _')
    if not (date_string[19] == '+' or date_string[19] == '-'):
        raise BadCLIArgument('Date expects + or -')