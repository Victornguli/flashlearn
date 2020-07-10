def to_bool(string):
	"""
	Convert 0/1 or true/false to Python bool type
	:param string: The string to be converted
	:type string: str
	"""
	if isinstance(string, str):
		try:
			number = int(string)
			if number == 0 or number == 1:
				return bool(number)
		except ValueError:
			pass
		if string == 'true' or string == 'false':
			return True if string == 'true' else False
	raise ValueError(f'{string} is not a valid string representation of a boolean value')
