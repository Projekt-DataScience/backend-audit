from typing import Union

import random

from fastapi import APIRouter, HTTPException, Header

from dao.recurrence import RecurrenceDAO
from backend_db_lib.models import LPAAuditRecurrence, User, Group, Layer
from db import dbm, RECURRENCE_TYPES, frontend_recurrence_value_to_backend_recurrence_value, \
    backend_to_frontend_recurrence_value
from helpers.auth import validate_authorization, get_user
from helpers.planned import fill_rhytm

router = APIRouter(
    prefix="/api/audit/planned",
    tags=["planned"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
def get_rhytms(authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    token = authorization.replace("Bearer ", "")
    with dbm.create_session() as session:
        recurrences = session.query(LPAAuditRecurrence).all()

        response_recurrences = []
        for recurrence in recurrences:
            response_recurrences.append(fill_rhytm(session, recurrence, token))

    return response_recurrences


@router.get("/types")
def get_recurrence_types(authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    return RECURRENCE_TYPES.TYPES


@router.get("/values/{type}")
def get_recurrence_values(type: str, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    if type not in RECURRENCE_TYPES.TYPES:
        raise HTTPException(status_code=404, detail="Recurrence type is invalid")

    return RECURRENCE_TYPES.VALUES[type]


@router.get("/{id}")
def get_rhytm(id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        recurrence = session.query(LPAAuditRecurrence).get(id)
        if recurrence is None:
            raise HTTPException(status_code=404)

        recurrence_response = fill_rhytm(session, recurrence, authorization.replace("Bearer ", ""))

    return recurrence_response

@router.get("/user/{user_id}")
def get_rhytm_by_user_id(user_id: int, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)

    recurrence_response = []
    with dbm.create_session() as session:
        recurrences = session.query(LPAAuditRecurrence).filter(LPAAuditRecurrence.auditor_id == user_id).all()
        if recurrences is not None and len(recurrences) > 0:
            for recurrence in recurrences:
                recurrence_response.append(fill_rhytm(session, recurrence, authorization.replace("Bearer ", "")))
        else:
            user = get_user(session, user_id)
            group = user.get("group")
            group_id = None
            if group:
                group_id = group.get("id")
            
            layer = user.get("layer")
            layer_id = None
            if layer:
                layer_id = layer.get("id")

            if layer_id is not None and group_id is not None:
                recurrences = session.query(LPAAuditRecurrence).filter(LPAAuditRecurrence.group_id == group_id, LPAAuditRecurrence.layer_id == layer_id).all()
            elif layer_id is not None:
                recurrences = session.query(LPAAuditRecurrence).filter(LPAAuditRecurrence.layer_id == layer_id).all()
            elif group_id is not None:
                recurrences = session.query(LPAAuditRecurrence).filter(LPAAuditRecurrence.group_id == group_id).all()
            
            if recurrences is not None and len(recurrences) > 0:
                for recurrence in recurrences:
                    recurrence_response.append(fill_rhytm(session, recurrence, authorization.replace("Bearer ", "")))

    return recurrence_response

@router.post("")
def create_rhytm(recurrence: RecurrenceDAO, authorization: Union[str, None] = Header(default=None)):
    payload = validate_authorization(authorization)
    with dbm.create_session() as session:
        auditor = session.query(User).get(recurrence.auditor_id)
        if auditor is None:
            raise HTTPException(status_code=404, detail="Auditor not found")

        group = session.query(Group).get(recurrence.group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        layer = session.query(Layer).get(recurrence.layer_id)
        if layer is None:
            raise HTTPException(status_code=404, detail="Layer not found")

        if recurrence.recurrence_type not in RECURRENCE_TYPES.TYPES:
            raise HTTPException(status_code=404, detail="Recurrence type is invalid")

        if recurrence.question_count <= 0:
            raise HTTPException(status_code=400, detail="Question count is invalid")

        value = frontend_recurrence_value_to_backend_recurrence_value(
            recurrence.recurrence_type,
            recurrence.values
        )

        r = LPAAuditRecurrence(
            auditor_id=recurrence.auditor_id,
            group_id=recurrence.group_id,
            layer_id=recurrence.layer_id,
            type=recurrence.recurrence_type,
            question_count=recurrence.question_count,
            value=value
        )

        session.add(r)
        session.flush()
        session.commit()
        session.refresh(r)

    response = RecurrenceDAO(
        id=r.id,
        auditor_id=r.auditor_id,
        group_id=r.group_id,
        layer_id=r.layer_id,
        question_count=r.question_count,
        recurrence_type=r.type,
        values=backend_to_frontend_recurrence_value(r.type, r.value)
    )

    return response
