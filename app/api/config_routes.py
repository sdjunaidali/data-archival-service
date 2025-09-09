from fastapi import APIRouter, Depends, HTTPException
from app.schemas.config_schema import ConfigRequest, ConfigResponse
from app.core.config_manager import set_config, get_config_by_table, get_all_configs
from app.core.security import get_current_active_user, is_admin_or_table_access

router = APIRouter(prefix="/config", tags=["config"])

@router.post("/", response_model=ConfigResponse)
def set_cfg(cfg: ConfigRequest, user=Depends(get_current_active_user)):
    is_admin_or_table_access(user, cfg.table_name)
    return set_config(cfg)

@router.get("/{table_name}", response_model=ConfigResponse)
def get_cfg(table_name: str, user=Depends(get_current_active_user)):
    is_admin_or_table_access(user, table_name)
    cfg = get_config_by_table(table_name)
    if not cfg:
        raise HTTPException(status_code=404, detail="Not found")
    return cfg

@router.get("/", response_model=list[ConfigResponse])
def list_cfgs(user=Depends(get_current_active_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return get_all_configs()