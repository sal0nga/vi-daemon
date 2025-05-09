try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Older Python: needs `pip install tomli`

from pathlib import Path

class Config:
    def __init__(self):
        # Defaults
        self.scan_interval = 10
        self.enable_sqlite_logging = True
        self.alert_thresholds = {
            'new_ips_per_minute': 5
        }

        self._validate()

        # Load overrides from settings.toml
        cfg_path = Path.home() / '.vi' / 'config' / 'settings.toml'
        if cfg_path.exists():
            with open(cfg_path, 'rb') as f:
                data = tomllib.load(f)
            # Top-level entries
            self.scan_interval = int(data.get('scan_interval', self.scan_interval))
            self.enable_sqlite_logging = bool(data.get('enable_sqlite_logging', self.enable_sqlite_logging))
            # Nested thresholds
            at = data.get('alert_thresholds', {})
            self.alert_thresholds['new_ips_per_minute'] = int(
                at.get('new_ips_per_minute', self.alert_thresholds['new_ips_per_minute'])
            )
    
    def _validate(self):
        if not isinstance(self.scan_interval, int) or self.scan_interval <= 0:
            raise ValueError(f"scan_interval must be a positive integer (got {self.scan_interval!r})")
        if not isinstance(self.enable_sqlite_logging, bool):
            raise ValueError(f"enable_sqlite_logging must be true/false (got {self.enable_sqlite_logging!r})")
        ip_th = self.alert_thresholds.get('new_ips_per_minute')
        if not isinstance(ip_th, int) or ip_th < 0:
            raise ValueError(f"alert_thresholds.new_ips_per_minute must be a non‐negative integer (got {ip_th!r})")
# Singleton instance
config = Config()