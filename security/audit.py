import logging

audit_logger = logging.getLogger("soclab.audit")


def audit_log(event: str, user: str = "anonymous", details: dict = None):
    audit_logger.info(f"AUDIT event={event} user={user} details={details or {}}")
