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
             ]

test_data1 = [("11FBAE00", {'field1': 'reserved',
                           'field2': '00',
                           'field3': '01',
                           'field4': '00',
                           'field5': '01',
                           'field6': '01',
                           'field7': '00',
                           'field8': 'Very High',
                           'field9': '00',
                           'field10': '01'}),
             ]

test_data2 = [("00000E00", {'field1': 'Low',
                            'field2': '00',
                            'field3': '00',
                            'field4': '00',
                            'field5': '00',
                            'field6': '00',
                            'field7': '00',
                            'field8': 'Very Low',
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


# Working on the payload to receive the parsed fields dict
def get_data_from_payload(payload):
    input_data = payload
    device_bytes = check_bytes(input_data)
    byte_array = interp_bytes(device_bytes)
    parsed_data = comparing_bits(byte_array)
    return parsed_data


# Splitting the payload input into the 4 bytes
def check_bytes(sting):
    index = 0
    bytes_dict = {}
    for _ in sting:
        index += 1
        if index > 0 and index % 2 == 0:
            byte_string = sting[index-2:index]
            bit_string = bin(int(byte_string, 16), )[2:]
            if len(bit_string) < 8:
                bit_string = str((8-len(bit_string)) * '0') + bit_string
            bytes_dict['byte_{}'.format(index//2)] = bit_string
    return bytes_dict


# Interpreting the bytes string into the fields according to the device_settings sample
def interp_bytes(dictionary):
    fields = {}
    for key in dictionary.keys():
        if key == 'byte_1':
            fields['field1'] = dictionary[key][5:]
            fields['field2'] = dictionary[key][4]
            fields['field3'] = dictionary[key][3]
            fields['field4'] = dictionary[key][:3]
        elif key == 'byte_2':
            fields['field5'] = dictionary[key][7]
            fields['field6'] = dictionary[key][6]
            fields['field7'] = dictionary[key][5]
            fields['field8'] = dictionary[key][2:5]
        elif key == 'byte_3':
            fields['field9'] = dictionary[key][7]
            fields['field10'] = dictionary[key][2]
    return fields


# Comparing the bits of interpreted bytes of the payload with the correct fields sample
def comparing_bits(result_dict):
    for key in result_dict.keys():
        if key == 'field1':
            if str(int(result_dict[key], 2)) in field1.keys():
                result_dict[key] = field1[str(int(result_dict[key], 2))]
        elif key == 'field4':
            if str(int(result_dict[key], 2)) in field4.keys():
                result_dict[key] = field4[str(int(result_dict[key], 2))]
        elif key == 'field8':
            if str(int(result_dict[key], 2)) in field8.keys():
                result_dict[key] = field8[str(int(result_dict[key], 2))]
        else:
            result_dict[key] = '0' + str(int(result_dict[key]))
    print(result_dict)
    return result_dict


# Loading 3 payload samples and 3 expected results
payload_data = [test_data[0][0], test_data1[0][0], test_data2[0][0]]
result_data = [test_data[0][1], test_data1[0][1], test_data2[0][1]]


# Testing the payload and the expected result with different params
@pytest.fixture(params=(
    (payload_data[0], result_data[0]),
    (payload_data[1], result_data[1]),
    (payload_data[2], result_data[2])),
    ids=['correct 10FA0E00 payload', 'correct 11FBAE00 payload', 'correct 00000E00 payload'])
def diff_params(request):
    return request.param


def test_result(diff_params):
    (goal, result) = diff_params
    assert get_data_from_payload(goal) == result
