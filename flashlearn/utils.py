def to_bool(inp):
    """
    Convert 0/1 or true/false to Python bool type
    :param inp: The string to be converted
    :type inp: str | bool | int
    """
    if isinstance(inp, str):
        inp = inp.lower()
    if inp in ["true", "1", 1, True]:
        return True
    elif inp in ["false", "0", 0, False]:
        return False
    raise ValueError(
        f"{inp} is not a valid string representation of a boolean value")
