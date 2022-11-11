from typing import List


def extract_bits(byte_data: int, target_len: int = 8) -> List[int]:
    """
    Extract bits from the bytes provided.

    :param byte_data: Source bytes as an integer .
    :param target_len: The desired bitstring length. Defaults to 8.
    :return: A list of integers of the target length.
        The members of the list are 0 and 1.
    """
    bin_num = bin(byte_data).lstrip("0b")
    bits = [int(bit) for bit in bin_num]
    if len(bits) < target_len:
        leading_bits = [0 for _ in range(target_len - len(bits))]
        bits = leading_bits + bits
    return bits
