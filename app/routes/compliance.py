from datetime import datetime

from flask import Blueprint, Response, jsonify, request

from app.services.compliance import check_concentration

bp = Blueprint("compliance", __name__)


@bp.route("/compliance/concentration", methods=["GET"])
def concentration() -> tuple[Response, int]:
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "'date' parameter is required"}), 400

    try:
        report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    violations = check_concentration(report_date)
    return jsonify(
        {
            "date": date_str,
            "violations_count": len(violations),
            "violations": violations,
        }
    ), 200
