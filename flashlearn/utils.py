def to_bool(string):
	"""
	Convert 0/1 or true/false to Python bool type
	:param string: The string to be converted
	:type string: str | bool
	"""
	if isinstance(string, str):
		try:
			number = int(string)
			if number == 0 or number == 1:
				return bool(number)
		except ValueError:
			pass
		if string.lower() == 'true' or string.lower() == 'false':
			return True if string == 'true' else False
	elif isinstance(string, bool):
		return string
	raise ValueError(f'{string} is not a valid string representation of a boolean value')
