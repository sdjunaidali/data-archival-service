from app.db.connection import get_source_session
from app.models.archival_config import ArchivalConfig
from app.schemas.config_schema import ConfigRequest, ConfigResponse

def set_config(cfg: ConfigRequest) -> ConfigResponse:
    db = get_source_session()
    m = db.query(ArchivalConfig).filter(ArchivalConfig.table_name == cfg.table_name).first()
    if m:
        m.archive_after_days = cfg.archive_after_days
        m.delete_after_days = cfg.delete_after_days
        m.custom_criteria = cfg.custom_criteria
    else:
        m = ArchivalConfig(**cfg.dict())
        db.add(m)
    db.commit(); db.refresh(m); db.close()
    return ConfigResponse.model_validate(m)

def get_config_by_table(table_name: str):
    db = get_source_session()
    m = db.query(ArchivalConfig).filter(ArchivalConfig.table_name == table_name).first()
    db.close()
    return ConfigResponse.model_validate(m) if m else None

def get_all_configs(as_session=False):
    db = get_source_session()
    items = db.query(ArchivalConfig).all()
    if as_session:
        return items
    res = [ConfigResponse.model_validate(i) for i in items]
    db.close()
    return res