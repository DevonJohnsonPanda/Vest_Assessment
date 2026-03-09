from flask import Blueprint, Response, jsonify, request

from app.ingestion import detect_and_parse

bp = Blueprint("ingest", __name__)


@bp.route("/ingest", methods=["POST"])
def ingest() -> tuple[Response, int]:
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"error": "No filename"}), 400

    content = uploaded.read().decode("utf-8")
    report = detect_and_parse(content, uploaded.filename)
    return jsonify(report), 200
