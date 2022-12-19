from backend_db_lib.models import LPAAuditRecurrence
from backend_db_lib.recurrence import RecurrenceHelper

from dao.recurrence import ResponseRecurrenceDAO
from helpers.auth import get_group, get_layer, get_user

def fill_rhytm(session, rhytm: LPAAuditRecurrence, token: str) -> ResponseRecurrenceDAO:
    group = get_group(rhytm.group_id, token)
    layer = get_layer(rhytm.layer_id, token)
    auditor = get_user(session, rhytm.auditor_id)

    values = RecurrenceHelper.backend_to_frontend_recurrence_value(rhytm.type, rhytm.value)


    return ResponseRecurrenceDAO(
        id=rhytm.id,
        auditor=auditor,
        group=group,
        layer=layer,
        question_count=rhytm.question_count,
        recurrence_type=rhytm.type,
        values=values,
    )

