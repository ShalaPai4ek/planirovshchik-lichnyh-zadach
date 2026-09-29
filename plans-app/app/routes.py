from flask import jsonify, request
from sqlalchemy import select
from database import SessionLocal
from models import Event
from datetime import datetime


def validate_event(data):
    required_fields = [
        "title",
        "description",
        "start_at",
        "end_at"
    ]

    for field in required_fields:
        if field not in data:
            return f"{field} is required"

    return None


def register_routes(app):
    @app.route("/api/hello", methods=["GET"])
    def hello():
        return jsonify({
            "message": "Hello from API!"
        })


    @app.route("/api/events", methods=["GET"])
    def get_events():
        with SessionLocal() as session:
            result = session.execute(
                    select(Event)
            )

            events = result.scalars().all()

        return jsonify([
            {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat()
            }
            for event in events
        ])


    @app.route("/api/events/<int:event_id>", methods=["GET"])
    def get_event(event_id):
        with SessionLocal() as session:
            event = session.get(Event, event_id)
        
        if event is None:
            return jsonify({
                "error": "Event not found"
            }), 404

        return jsonify(
            {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat()
            }
        )


    @app.route("/api/events", methods=["POST"])
    def create_event():
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        error = validate_event(data)

        if error:
            return jsonify({
                "error": error
            }), 400

        start_at = datetime.fromisoformat(data["start_at"])
        end_at = datetime.fromisoformat(data["end_at"])

        new_event = Event(
            title=data["title"],
            description=data["description"],
            start_at=start_at,
            end_at=end_at
        )
        
        with SessionLocal() as session:
            session.add(new_event)
            session.commit()

            return jsonify({
                "id": new_event.id,
                "title": new_event.title,
                "description": new_event.description,
                "start_at": new_event.start_at.isoformat(),
                "end_at": new_event.end_at.isoformat()
            }), 201


    @app.route("/api/events/<int:event_id>", methods=["PUT"])
    def update_event(event_id):
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        error = validate_event(data)

        if error:
            return jsonify({
                "error": error
            }), 400

        start_at = datetime.fromisoformat(data["start_at"])
        end_at = datetime.fromisoformat(data["end_at"])
        
        with SessionLocal() as session:
            event = session.get(Event, event_id)

            if event is None:
                return jsonify({
                    "error": "Event not found"
                }), 404

            event.title = data["title"]
            event.description = data["description"]
            event.start_at = start_at
            event.end_at = end_at

            session.commit()

            return jsonify({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat()
            })


    @app.route("/api/events/<int:event_id>", methods=["DELETE"])
    def delete_event(event_id):
        with SessionLocal() as session:
            event = session.get(Event, event_id)
        
            if event is None:
                return jsonify({
                    "error": "Event not found"
                }), 404
            
            session.delete(event)
            session.commit()

        return jsonify({
            "message": "Event deleted"
        })
