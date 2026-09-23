from flask import jsonify, request

events = [
    {
        "id": 1,
        "title": "Математика",
        "description": "Подготовиться к контрольной",
        "start_at": "2026-09-25T10:00:00",
        "end_at": "2026-09-25T11:30:00"
     },
     {
         "id": 2,
         "title": "Встреча",
         "description": "Встреча с друзьями",
         "start_at": "2026-09-26T18:00:00",
         "end_at": "2026-09-26T20:00:00"
     }
]

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
        return jsonify(events)

    @app.route("/api/events/<int:event_id>", methods=["GET"])
    def get_event(event_id):
        for event in events:
            if event["id"] == event_id:
                return jsonify(event)
        return jsonify({
              "error": "Event not found"
        }), 404

    @app.route("/api/events", methods=["POST"])
    def create_event():
        data = request.get_json()
        error = validate_event(data)
        
        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        if error:
            return jsonify({
                "error": error
            }), 400

        new_event = {
            "id": len(events) + 1,
            "title": data["title"],
            "description": data["description"],
            "start_at": data["start_at"],
            "end_at": data["end_at"]
        }
                
        events.append(new_event)

        return jsonify(new_event), 201

    @app.route("/api/events/<int:event_id>", methods=["PUT"])
    def update_event(event_id):
        data = request.get_json()
        error = validate_event(data)

        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        if error:
            return jsonify({
                "error": error
            }), 400

        for event in events:
            if event["id"] == event_id:
                event["title"] = data["title"]
                event["description"] = data["description"]
                event["start_at"] = data["start_at"]
                event["end_at"] = data["end_at"]

                return jsonify(event)

        return jsonify({
            "error": "Event not found"
        }), 404

    @app.route("/api/events/<int:event_id>", methods=["DELETE"])
    def delete_event(event_id):

        for event in events:
            if event["id"] == event_id:
                events.remove(event)

                return jsonify({
                    "message": "Event deleted"
                })

        return jsonify({
            "error": "Event not found"
        }), 404
