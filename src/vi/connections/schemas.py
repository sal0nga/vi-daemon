from pydantic import BaseModel, Field

class ConnectionFeatures(BaseModel):
    cpu_percent: float = Field(..., ge=0.0, le=100.0)
    memory_rss_mb: float = Field(..., ge=0.0)
    connection_count: int = Field(..., ge=0)
    duration_seconds: float = Field(..., ge=0.0)
    is_remote_ipv6: int = Field(..., ge=0, le=1)

    class Config:
        schema_extra = {
            "example": {
                "cpu_percent": 0.05,
                "memory_rss_mb": 50.0,
                "connection_count": 2,
                "duration_seconds": 300.0,
                "is_remote_ipv6": 0
            }
        }