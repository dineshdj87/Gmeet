import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date

# -------------------------
# Minimal sanity imports
# -------------------------
# Ensure Attendance doctype has a 'last_heartbeat' Datetime field (recommended).

@frappe.whitelist()
def ping():
    """Simple ping test"""
    return "pong from liveclass_monitor2"


# -------------------------
# Create Focus Session
# -------------------------
@frappe.whitelist()
def create_focus_session(teacher, classroom):
    if not frappe.db.exists("Teacher", teacher):
        frappe.throw(_("Teacher does not exist"))
    if not frappe.db.exists("Classroom", classroom):
        frappe.throw(_("Classroom does not exist"))

    session = frappe.get_doc({
        "doctype": "Focus Session",
        "teacher": teacher,
        "classroom": classroom,
        "status": "Active"
    })
    session.insert(ignore_permissions=True)

    # Initialize attendance rows for students in class
    student_count = initialize_attendance(session.name)

    frappe.db.commit()
    return {
        "message": "Focus session created",
        "session_id": session.name,
        "student_count": student_count
    }


# -------------------------
# Initialize attendance
# -------------------------
def initialize_attendance(session_id):
    classroom = frappe.db.get_value("Focus Session", session_id, "classroom")
    students = frappe.get_all("Student", filters={"class": classroom}, pluck="name")

    for s in students:
        # avoid duplicate insert
        if not frappe.db.exists("Attendance", {"student": s, "focus_session": session_id}):
            frappe.get_doc({
                "doctype": "Attendance",
                "student": s,
                "focus_session": session_id,
                "status": "Absent"
            }).insert(ignore_permissions=True)

    return len(students)


# -------------------------
# Update student status (heartbeat / join / left / idle)
# -------------------------
@frappe.whitelist(allow_guest=True)
def update_student_status(student, session_id, status):
    """
    Updates or creates Attendance for the student+session.
    Also publishes a realtime event so teacher dashboard updates instantly.

    status: "Active", "Idle", "Left App", "Absent"
    """
    now = now_datetime()

    # Lookup attendance for this session/student
    att_name = frappe.db.get_value(
        "Attendance",
        {"student": student, "focus_session": session_id},
        "name"
    )

    if not att_name:
        # Create attendance if missing
        att = frappe.get_doc({
            "doctype": "Attendance",
            "student": student,
            "focus_session": session_id,
            "status": status,
            "joined_at": now if status == "Active" else None,
            "left_at": now if status == "Left App" else None,
            # last_heartbeat is recommended to exist in doctype
            "last_heartbeat": now
        })
        att.insert(ignore_permissions=True)
    else:
        att = frappe.get_doc("Attendance", att_name)
        att.status = status

        # set joined_at when first Active
        if status == "Active" and not att.joined_at:
            att.joined_at = now

        # set left_at when left
        if status == "Left App":
            att.left_at = now

        # update last_heartbeat for Active/Idle heartbeats
        att.last_heartbeat = now
        att.save(ignore_permissions=True)

    # persist immediately so realtime readers see correct data
    frappe.db.commit()

    # publish realtime event (teacher dashboard listens for this)
    frappe.publish_realtime(
        event="student_status_change",
        message={
            "student": student,
            "session_id": session_id,
            "status": status,
            "time": now.strftime("%H:%M:%S")
        }
    )

    return {"message": "Status updated", "student": student, "status": status}


# -------------------------
# Start focus session helper (creates attendance rows)
# -------------------------
@frappe.whitelist()
def start_focus_session(session_id):
    session = frappe.get_doc("Focus Session", session_id)

    if session.status != "Active":
        session.status = "Active"
        session.save()

    students = frappe.get_all("Student", filters={"class": session.classroom}, pluck="name")

    for s in students:
        if not frappe.db.exists("Attendance", {"student": s, "focus_session": session_id}):
            frappe.get_doc({
                "doctype": "Attendance",
                "student": s,
                "focus_session": session_id,
                "status": "Absent"
            }).insert(ignore_permissions=True)

    frappe.db.commit()
    return {"message": "Session started"}


# -------------------------
# Helper: Mark dead / timed-out students
# -------------------------
def mark_dead_students(timeout_seconds=70):
    """
    Find Attendance rows where last_heartbeat older than now - timeout_seconds
    and status is not Left App / Absent, then mark them as 'Left App'.
    Call this periodically (cron / scheduler).
    """
    cutoff = add_to_date(now_datetime(), hours=0, seconds=-timeout_seconds)

    # This query assumes Attendance has last_heartbeat field. If not present, add it to doctype.
    rows = frappe.db.sql("""
        SELECT name, student, focus_session, status
        FROM `tabAttendance`
        WHERE ifnull(last_heartbeat, '1970-01-01 00:00:00') < %s
          AND status NOT IN ('Left App', 'Absent')
    """, (cutoff,), as_dict=True)

    changed = []
    for r in rows:
        try:
            att = frappe.get_doc("Attendance", r.name)
            att.status = "Left App"
            att.left_at = now_datetime()
            att.save(ignore_permissions=True)
            changed.append((att.student, att.focus_session))
            # publish realtime event
            frappe.publish_realtime(
                "student_status_change",
                {"student": att.student, "session_id": att.focus_session, "status": "Left App", "time": now_datetime().strftime("%H:%M:%S")}
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "mark_dead_students")

    frappe.db.commit()
    return {"marked": len(changed), "details": changed}

