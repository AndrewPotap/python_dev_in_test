import pytest


TEST_PROCESSING_DATA = [(-180, "180^0W"), (-180.0, "180^0W"), (170.1, "170^6E"), (16.053, "16^3.18E"),
                        (120.00973, "120^0.584E"), (-141.0233, "141^1.398W")]


def loading_payload(payload):
    dd_list, ddm_list = [], []
    for pair in payload:
        dd_list.append(pair[0])
        ddm_list.append(pair[1])
    payload_data = zip(dd_list, ddm_list)
    return payload_data, dd_list


def coordinates_convert(dd_coordinate):
    first_part = abs(int(dd_coordinate))
    second_part = round(float(abs(dd_coordinate) - first_part) * 60, 3)
    if second_part.is_integer():
        second_part = int(second_part)
    third_part = "W" if dd_coordinate < 0 else "E"
    return f'{first_part}^{second_part}{third_part}'


received_payload = loading_payload(TEST_PROCESSING_DATA)


@pytest.fixture(params=received_payload[0], ids=received_payload[1])
def diff_params(request):
    return request.param


def test_result(diff_params):
    (goal, result) = diff_params
    assert coordinates_convert(goal) == result
