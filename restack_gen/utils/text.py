import re

def snake_case(name: str) -> str:
	"""Convert string to snake_case."""
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def pascal_case(name: str) -> str:
	"""Convert string to PascalCase."""
	return ''.join(word.capitalize() for word in snake_case(name).split('_'))

def kebab_case(name: str) -> str:
	"""Convert string to kebab-case."""
	return snake_case(name).replace('_', '-')
