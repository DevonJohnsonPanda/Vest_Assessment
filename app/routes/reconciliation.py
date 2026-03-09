from datetime import datetime

from flask import Blueprint, Response, jsonify, request

from app.services.reconciliation import reconcile

bp = Blueprint("reconciliation", __name__)


@bp.route("/reconciliation", methods=["GET"])
def reconciliation() -> tuple[Response, int]:
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "'date' parameter is required"}), 400

    try:
        report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    result = reconcile(report_date)
    return jsonify(result), 200
