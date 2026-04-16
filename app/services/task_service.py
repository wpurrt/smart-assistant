from app.extensions import db
from app.models import ActionLog


def log_user_action(user_id, action_type, entity_type, description):
    log = ActionLog(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        description=description
    )
    db.session.add(log)