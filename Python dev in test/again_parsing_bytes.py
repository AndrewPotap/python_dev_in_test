import pytest

test_data = [("10FA0E00", {'field1': 'Low',
                           'field2': '00',
                           'field3': '01',
                           'field4': '00',
                           'field5': '00',
                           'field6': '01',
                           'field7': '00',
                           'field8': 'Very High',
                           'field9': '00',
                           'field10': '00'}),
             ("10FAAE00", {'field1': 'Low',
                           'field2': '00',
                           'field3': '01',
                           'field4': '00',
                           'field5': '00',
                           'field6': '01',
                           'field7': '00',
                           'field8': 'Very High',
                           'field9': '00',
                           'field10': '01'}),
             ("05BC8E00", {'field1': 'Low',
                           'field2': '00',
                           'field3': '01',
                           'field4': '00',
                           'field5': '00',
                           'field6': '01',
                           'field7': '00',
                           'field8': 'Very High',
                           'field9': '00',
                           'field10': '00'}),
             ]

# Format settings - array [sett_byte1 as dict {bit: [size, 'field_name']}, sett_byte2, sett_byte3, sett_byte4]
device_settings = [{0: [3, 'field1'],
                    3: [1, 'field2'],
                    4: [1, 'field3'],
                    5: [3, 'field4']},
                   {0: [1, 'field5'],
                    1: [1, 'field6'],
                    2: [1, 'field7'],
                    3: [3, 'field8'],
                    },
                   {0: [1, 'field9'],
                    5: [1, 'field10']
                    },
                   {}
                   ]

field1 = {'0': 'Low',
          '1': 'reserved',
          '2': 'reserved',
          '3': 'reserved',
          '4': 'Medium',
          '5': 'reserved',
          '6': 'reserved',
          '7': 'High',
          }
field4 = {'0': '00',
          '1': '10',
          '2': '20',
          '3': '30',
          '4': '40',
          '5': '50',
          '6': '60',
          '7': '70',
          }
field8 = {'0': 'Very Low',
          '1': 'reserved',
          '2': 'Low',
          '3': 'reserved',
          '4': 'Medium',
          '5': 'High',
          '6': 'reserved',
          '7': 'Very High',
          }
# All the extended fields should be added here in sorted order
EXTENDED_FIELDS = (field1, field4, field8)


def create_payload(test_values):
    """
    Creates payload data from the test data
    :param test_values: it is the test data set, should be crated by the TESTER
    :return: payload string and the expected result, list of the byte strings for PyTest fixture
    """
    string_data = []
    result_data = []
    for strings, results in test_values:
        string_data.append(strings)
        result_data.append(results)
    payload_data = zip(string_data, result_data)
    return payload_data, string_data


def parsing_bytes(payload):
    """
    Parses the byte string to the bits
    :param payload: string of bytes -- payload string
    :return: dictionary of bit strings by number of byte
    """
    index = 0
    parsed_bits_dict = {}
    # Checking for the bytes amount and supplementing the string if necessary
    if len(payload) % 2 != 0:
        payload = payload.zfill(len(payload) + 1)
    for _ in payload:
        index += 1
        if index % 2 == 0:
            # Converting the payload string to the 10-base int
            bit_string = int(payload[index - 2:index], 16)
            # Converting the same string to the binary string and completing it with zeros
            bit_string = bin(bit_string)[2:].zfill(8)
            # Creating the dictionary of parsed bytes string
            parsed_bits_dict[index // 2] = bit_string
    return parsed_bits_dict


def dict_collocations(bits_dict, settings_dict):
    """
    Receives the parsed bits and correlates them with the fields of the device's settings
    :param bits_dict: parsed dictionary of bits by number of byte
    :param settings_dict: should be created by the Tester, the form of device's settings
    :return: the list of compared FIELD values
    """
    values_list, fields = [], []
    # Correlate the FIELD value with the parsed bytes
    for some_dict, number in zip(settings_dict, range(1, len(settings_dict) + 1)):
        for key in some_dict:
            # Checking the size of the FIELD (the size of NULL cell)
            if some_dict[key][0] > 1:
                sliced = bits_dict[number][key:key + some_dict[key][0]]
                fields.append(sliced)
                # If the FIELD size > 1, than correlate FIELD value according to the expanded descriptions
                for field, real_field in zip(fields, EXTENDED_FIELDS):
                    some_dict[key][1] = real_field[str(int(field, 2))]
            else:
                some_dict[key][1] = bits_dict[number][key].zfill(2)
            values_list.append(some_dict[key][1])
    return values_list


def get_parameters(payload_string):
    """
    Runs the parsing and collocation functions and prints the dictionary of parsed parameters by fields
    :param payload_string: the byte string -- the payload string
    :return: the dictionary of parsed parameters by fields
    """
    parsed_bytes = parsing_bytes(payload_string)
    # Reversing the bit strings for correct collocation
    for key, value in parsed_bytes.items():
        parsed_bytes[key] = value[::-1]
    parsed_parameters = dict_collocations(parsed_bytes, device_settings)
    # Creating the parameters dictionary according to the parsed payload string
    parameters_dict = {f'field{field_number}': item for item, field_number in
                       zip(parsed_parameters, range(1, len(parsed_parameters) + 1))}
    # Printing the parsed parameters
    print(parameters_dict)
    return parameters_dict


@pytest.fixture(params=create_payload(test_data)[0],
                ids=create_payload(test_data)[1])
def diff_params(request):
    return request.param


def test_result(diff_params):
    (goal, result) = diff_params
    assert get_parameters(goal) == result
