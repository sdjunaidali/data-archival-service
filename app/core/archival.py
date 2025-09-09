import json
from datetime import datetime, timedelta, date
from sqlalchemy import text
from app.db.connection import get_source_session, get_archive_session
from app.models.archived_data import ArchivedData
from app.core.config_manager import get_all_configs

from decimal import Decimal

def to_jsonable(d: dict):
    out = {}
    for k, v in d.items():
        if isinstance(v, (datetime, date)):
            out[k] = v.isoformat()
        elif isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out

def archive_and_delete_job():
    src = get_source_session(); dst = get_archive_session()
    now = datetime.utcnow()
    for cfg in get_all_configs(as_session=True):
        cutoff_archive = now - timedelta(days=cfg.archive_after_days)
        cutoff_delete = now - timedelta(days=cfg.delete_after_days)

        select_sql = f"SELECT * FROM {cfg.table_name} WHERE created_at < :cutoff"
        if cfg.custom_criteria:
            select_sql += f" AND {cfg.custom_criteria}"
        
        rows = src.execute(text(select_sql), {"cutoff": cutoff_archive}).fetchall()
        if rows:
            for r in rows:
                row_dict = dict(r._mapping)
                row_dict = to_jsonable(row_dict)
                dst.add(ArchivedData(
                        table_name=cfg.table_name,
                        data=json.dumps(row_dict),
                        archived_at=now
                ))
            dst.commit()

            ids = [r._mapping.get("id") for r in rows if "id" in r._mapping]
            if ids:
                src.execute(text("DELETE FROM {t} WHERE id = ANY(:ids)".format(t=cfg.table_name)), {"ids": ids})
                src.commit()

    src.close(); dst.close()

def purge_expired_archives():
    dst = get_archive_session()
    now = datetime.utcnow()
    try:
        for cfg in get_all_configs(as_session=True):
            cutoff_delete = now - timedelta(days=cfg.delete_after_days)
            dst.execute(
                text("DELETE FROM archived_data WHERE table_name=:t AND archived_at < :delcut"),
                {"t": cfg.table_name, "delcut": cutoff_delete},
            )
        dst.commit()
    finally:
        dst.close()

def fetch_archived_data(table_name: str):
    dst = get_archive_session()
    rows = dst.query(ArchivedData).filter(ArchivedData.table_name == table_name).order_by(ArchivedData.archived_at.desc()).all()
    dst.close()
    return [{"data": r.data, "archived_at": r.archived_at.isoformat()} for r in rows]