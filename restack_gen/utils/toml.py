from pathlib import Path
from typing import Any, Optional

class TOMLLoader:
	"""Handles TOML file loading with fallback support."""
	_lib = None
	_checked = False
	@classmethod
	def _get_lib(cls):
		"""Get TOML library with caching."""
		if cls._checked:
			return cls._lib
		cls._checked = True
		try:
			import tomllib
			cls._lib = ('tomllib', tomllib)
		except ImportError:
			try:
				import toml
				cls._lib = ('toml', toml)
			except ImportError:
				cls._lib = None
		return cls._lib
	@classmethod
	def load(cls, path: Path) -> dict[str, Any]:
		"""Load TOML file."""
		if not path.exists():
			raise FileNotFoundError(f"TOML file not found: {path}")
		lib = cls._get_lib()
		if lib is None:
			raise ValueError(
				"No TOML library available. Install with: pip install tomli"
			)
		lib_name, lib_module = lib
		try:
			if lib_name == 'tomllib':
				with open(path, 'rb') as f:
					return lib_module.load(f)
			else:
				return lib_module.load(path)
		except Exception as e:
			raise ValueError(f"Failed to parse TOML: {e}")
	@classmethod
	def is_available(cls) -> bool:
		"""Check if TOML library is available."""
		return cls._get_lib() is not None
