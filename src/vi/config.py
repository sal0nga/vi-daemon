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
        
        # Intel defaults
        self.intel = {
            'abuseipdb_api_key': None,
            'cache_ttl': 86400,
            'threshold_score': 50
        }

        # Notification defaults
        self.notifications = {
            'enable_desktop': True,
            'notifier': 'terminal-notifier',
            'min_severity': 'medium'
        }

        # Behavior toggles defaults
        self.behavior = {
            'alert_new_process': True,
            'alert_new_process_port': True
        }

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

            # Intel overrides from settings.toml
            intel_cfg = data.get('intel', {})
            self.intel['abuseipdb_api_key'] = intel_cfg.get('abuseipdb_api_key', self.intel['abuseipdb_api_key'])
            self.intel['cache_ttl'] = int(intel_cfg.get('cache_ttl', self.intel['cache_ttl']))
            self.intel['threshold_score'] = int(intel_cfg.get('threshold_score', self.intel['threshold_score']))

            # Notification overrides from settings.toml
            notif_cfg = data.get('notifications', {})
            self.notifications['enable_desktop'] = bool(
                notif_cfg.get('enable_desktop', self.notifications['enable_desktop'])
            )
            self.notifications['notifier'] = notif_cfg.get(
                'notifier', self.notifications['notifier']
            )
            self.notifications['min_severity'] = notif_cfg.get(
                'min_severity', self.notifications['min_severity']
            )

            # Behavior toggles overrides from settings.toml
            beh = data.get('behavior', {})
            self.behavior['alert_new_process'] = bool(
                beh.get('alert_new_process', self.behavior['alert_new_process'])
            )
            self.behavior['alert_new_process_port'] = bool(
                beh.get('alert_new_process_port', self.behavior['alert_new_process_port'])
            )
        
        # Validate loaded configuration
        self._validate()
    
    def _validate(self):
        if not isinstance(self.scan_interval, int) or self.scan_interval <= 0:
            raise ValueError(f"scan_interval must be a positive integer (got {self.scan_interval!r})")
        if not isinstance(self.enable_sqlite_logging, bool):
            raise ValueError(f"enable_sqlite_logging must be true/false (got {self.enable_sqlite_logging!r})")
        ip_th = self.alert_thresholds.get('new_ips_per_minute')
        if not isinstance(ip_th, int) or ip_th < 0:
            raise ValueError(f"alert_thresholds.new_ips_per_minute must be a non‐negative integer (got {ip_th!r})")
        
        # Validate intel settings
        if not isinstance(self.intel['cache_ttl'], int) or self.intel['cache_ttl'] <= 0:
            raise ValueError(f"intel.cache_ttl must be a positive integer (got {self.intel['cache_ttl']!r})")
        if not isinstance(self.intel['threshold_score'], int) or not (0 <= self.intel['threshold_score'] <= 100):
            raise ValueError(f"intel.threshold_score must be between 0 and 100 (got {self.intel['threshold_score']!r})")
        
        # Validate notifications settings
        if not isinstance(self.notifications['enable_desktop'], bool):
            raise ValueError(f"notifications.enable_desktop must be true/false (got {self.notifications['enable_desktop']!r})")
        if not isinstance(self.notifications['notifier'], str):
            raise ValueError(f"notifications.notifier must be a string (got {self.notifications['notifier']!r})")
        if self.notifications['min_severity'] not in {'low', 'medium', 'high'}:
            raise ValueError(f"notifications.min_severity must be 'low', 'medium', or 'high' (got {self.notifications['min_severity']!r})")

        # Validate behavior toggles
        if not isinstance(self.behavior['alert_new_process'], bool):
            raise ValueError(f"behavior.alert_new_process must be true/false (got {self.behavior['alert_new_process']!r})")
        if not isinstance(self.behavior['alert_new_process_port'], bool):
            raise ValueError(f"behavior.alert_new_process_port must be true/false (got {self.behavior['alert_new_process_port']!r})")

# Singleton instance
config = Config()