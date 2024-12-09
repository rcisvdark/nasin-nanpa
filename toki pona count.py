def number_to_nasin_nanpa(n: int | float, *, pona: bool = True, ali: bool = False, nimisuli: bool = True) -> str:
    """
        Convert a given number to its representation in Toki Pona's extended numerical system.

        Parameters:
        n : int | float
            The number to convert. Can be a positive or negative integer or float.

        pona : bool, optional, default=True
            If True, optimizes the representation for readability by grouping into larger units (e.g., hundreds, twenties).
            If False, represents the number with repeated smaller units.

        ali : bool, optional, default=False
            If True, uses 'ali' as the word for 100 (instead of 'ale') in the representation.

        nimisuli : bool, optional, default=True
            If True, uses descriptive words for numbers (e.g., 'wan', 'luka', 'mute').
            If False, uses abbreviations (e.g., 'W', 'L', 'M').

        Returns:
        str
            The Toki Pona-style representation of the input number.

        Special Behavior:
        - Negative numbers are prefixed with 'weka '.
        - Decimal numbers are separated by 'ala ' (or '.' if nimisuli=False) and recursively converted.
        - Numbers over 100 are handled based on the `pona` and `ali` parameters:
            - When pona=True, hundreds are grouped with a prefix indicating the count.
            - When pona=False, hundreds are expressed as repeated units.
        - The representation is truncated when sequences of repeated patterns (e.g., 'ale ', 'ali ') exceed a threshold.
    """
    def transform_float(value):
        try:
            decimal_part = (value - int(value)) * 10**len(str(value).split(".")[1])
            result = int(decimal_part)
            return result
        except IndexError:
            return value

    def account_for_floating_point_precision_errors(input_string: str, threshold: int) -> str:
        if 'ala' in input_string:
            start_index = input_string.index('ala')
        elif '.' in input_string:
            start_index = input_string.index('.')
        else:
            return input_string

        substring = input_string[start_index:]

        patterns = ['ale ' * threshold, 'ali ' * threshold, 'A' * threshold]

        for pattern in patterns:
            if pattern in substring:
                cut_index = substring.index(pattern)
                return input_string[:start_index + cut_index]

        return input_string

    nimi_nanpa = ''

    if n<0:
        nimi_nanpa += 'weka '
        n *= -1

    integer_part = int(n)
    decimal_part = n-integer_part

    if integer_part >= 100:
        if pona:
            count = integer_part // 100
            integer_part %= 100
            nimi_nanpa += (
                    number_to_nasin_nanpa(count, pona=pona, ali=ali, nimisuli=nimisuli) +
                    f"{' ' if nimisuli else ''}{f'al{'i' if ali else 'e'} ' if nimisuli else 'A'}")
        else:
            count = integer_part // 100
            integer_part %= 100
            nimi_nanpa += f"{f'al{'i' if ali else 'e'} ' if nimisuli else 'A'}" * count

    if integer_part >= 20:
        count = integer_part // 20
        integer_part %= 20
        nimi_nanpa += f"{'mute ' if nimisuli else 'M'}" * count

    if integer_part >= 5:
        count = integer_part // 5
        integer_part %= 5
        nimi_nanpa += f"{'luka ' if nimisuli else 'L'}" * count

    if integer_part >= 2:
        count = integer_part // 2
        integer_part %= 2
        nimi_nanpa += f"{'tu ' if nimisuli else 'T'}" * count

    if integer_part >= 1:
        count = integer_part // 1
        integer_part %= 1
        nimi_nanpa += f"{'wan ' if nimisuli else 'W'}" * count

    if decimal_part>0:
        nimi_nanpa += 'ala ' if nimisuli else '.'
        nimi_nanpa += number_to_nasin_nanpa(transform_float(decimal_part), pona=pona, ali=ali, nimisuli=nimisuli)

    nimi_nanpa = account_for_floating_point_precision_errors(nimi_nanpa, threshold=5)

    return nimi_nanpa.rstrip() if nimi_nanpa else 'ala'


def nasin_nanpa_to_number(n: str, *, pona: bool = True) -> float:
    """
    Convert a Toki Pona-style extended numerical string into its numeric representation, with support for decimals.

    Parameters:
    n : str
        The Toki Pona-style numerical representation to convert.

    pona : bool, optional, default=True
        If True, interprets the number recursively based on the extended structure with 'ale' or 'ali'.
        If False, adds the values of all numbered words together directly.

    Returns:
    float
        The numeric value of the input string.
    """
    # Map descriptive words and abbreviations to their values
    numerals = {
        'wan': 1, 'tu': 2, 'luka': 5, 'mute': 20, 'ale': 100, 'ali': 100,
        'W': 1, 'T': 2, 'L': 5, 'M': 20, 'A': 100
    }
    if n == '':
        n='ala'

    # Detect nimisuli (descriptive or abbreviated)
    nimisuli = n[-1] not in {'W', 'T', 'L', 'M', 'A'}

    # Set separators and splitting method based on detected style
    if nimisuli:
        decimal_separator = 'ala '
        split_method = lambda s: s.split()  # Split by spaces
    else:
        decimal_separator = '.'
        split_method = lambda s: list(s)  # Split by each character

    # Check for 'weka' at the start and save that information
    is_negative = n.startswith('weka')
    if is_negative:
        n = n[len('weka '):]

    # Split into integer and decimal parts
    parts = n.split(decimal_separator)

    # Process integer part
    integer_part = parts[0].strip()
    total = 0

    if pona and ('ale' in integer_part or 'ali' in integer_part or 'A' in integer_part):
        # Recursive handling of ale/ali or A
        words = split_method(integer_part)
        last_hundred_index = min(
            words[::-1].index('ale') if 'ale' in words else float('inf'),
            words[::-1].index('ali') if 'ali' in words else float('inf'),
            words[::-1].index('A') if 'A' in words else float('inf'),
        )
        last_hundred_index = len(words) - 1 - last_hundred_index
        before_hundred = words[:last_hundred_index]
        after_hundred = words[last_hundred_index + 1:]
        total += 100 * nasin_nanpa_to_number(' '.join(before_hundred), pona=pona)
        total += nasin_nanpa_to_number(' '.join(after_hundred), pona=pona)
    else:
        # Add up integer part values
        for word in split_method(integer_part):
            if word in numerals:
                total += numerals[word]

    # Handle decimal part if present
    if len(parts) > 1:
        decimal_part = parts[1].strip()
        decimal_value = 0
        if pona and ('ale' in decimal_part or 'ali' in decimal_part or 'A' in decimal_part):
            # Recursive handling of ale/ali or A
            words = split_method(decimal_part)
            last_hundred_index = min(
                words[::-1].index('ale') if 'ale' in words else float('inf'),
                words[::-1].index('ali') if 'ali' in words else float('inf'),
                words[::-1].index('A') if 'A' in words else float('inf'),
            )
            last_hundred_index = len(words) - 1 - last_hundred_index
            before_hundred = words[:last_hundred_index]
            after_hundred = words[last_hundred_index + 1:]
            decimal_value += 100 * nasin_nanpa_to_number(' '.join(before_hundred), pona=pona)
            decimal_value += nasin_nanpa_to_number(' '.join(after_hundred), pona=pona)
        else:
            # Add up decimal part values
            for word in split_method(decimal_part):
                if word in numerals:
                    decimal_value += numerals[word]

        # Normalize decimal to correct format
        power_of_ten = 10 ** len(str(int(decimal_value)))
        decimal_value /= power_of_ten

        total += decimal_value

    return -total if is_negative else total
