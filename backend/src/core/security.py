"""API Key 认证依赖。

当配置的 api_key 为空时自动跳过认证（开发模式），
否则要求请求携带 X-API-Key Header。
"""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(
    api_key: str | None = Security(_api_key_header),
) -> str | None:
    """校验 API Key，空配置时跳过（开发模式）。"""
    settings = get_settings()
    configured_key = settings.security.api_key

    # 开发模式：未配置 API Key 则跳过认证
    if not configured_key:
        return None

    if not api_key or api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 API Key",
        )
    return api_key


# 可作为全局依赖注入到 FastAPI app 或单个 router
api_key_dependency = Depends(verify_api_key)
