import jwt
from flask import current_app, jsonify, request
from sqlalchemy import select
from database import SessionLocal
from models import Event, User
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


ALLOWED_ICONS = {
    "📚",
    "📝",
    "✏️",
    "🎓",
    "💻",
    "🧮",
    "🔬",
    "🎨",
    "🎵",
    "⚽",
    "🏃",
    "🏠",
    "🍕",
    "☕",
    "🎮",
    "🎬",
    "✈️",
    "❤️",
    "⭐",
    "🔥"
}


def validate_event(data):
    required_fields = [
        "title",
        "icon",
        "description",
        "start_at",
        "end_at"
    ]

    for field in required_fields:
        if field not in data:
            return f"{field} is required"
    
    return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({
                "error": "Authorization header is required"
            }), 401

        if not token.startswith("Bearer "):
            return jsonify({
                "error": "Authorization header must use Bearer token"
            })

        token = token[7:]

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token has expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid token"
            }), 401

        user_id = payload["user_id"]

        with SessionLocal() as session:
            user = session.get(User, user_id)

        if user is None:
            return jsonify({
                "error": "User not found"
            }), 401

        return f(user, *args, **kwargs)

    return decorated


def register_routes(app):
    @app.route("/api/register", methods=["POST"])
    def register():
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        if "username" not in data:
            return jsonify({
                "error": "username is required"
            }), 400

        if "password" not in data:
            return jsonify({
                "error": "password is required"
            }), 400

        with SessionLocal() as session:
            result = session.execute(
                select(User).where(
                    User.username == data["username"]
                )
            )

            user = result.scalar_one_or_none()

            if user is not None:
                return jsonify({
                    "error": "Username is already exists"
                }), 409

            password_hash = generate_password_hash(data["password"])

            new_user = User(
                username=data["username"],
                password_hash=password_hash
            )

            session.add(new_user)
            session.commit()

            return jsonify({
                "id": new_user.id,
                "username": new_user.username
            }), 201


    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "JSON body is required"
            }), 400

        if "username" not in data:
            return jsonify({
                "error": "username is required"
            }), 400

        if "password" not in data:
            return jsonify({
                "error": "password is required"
            }), 400

        with SessionLocal() as session:
            result = session.execute(
                select(User).where(
                    User.username == data["username"]
                )
            )

            user = result.scalar_one_or_none()

            if user is None:
                return jsonify({
                    "error": "Invalid username or password"
                }), 401

            password_is_correct = check_password_hash(
                user.password_hash,
                data["password"]
            )

            if not password_is_correct:
                return jsonify({
                    "error": "Invalid username or password"
                }), 401

            token = jwt.encode(
                {
                    "user_id": user.id,
                    "exp": datetime.utcnow() + timedelta(hours=24)
                },
                app.config["SECRET_KEY"],
                algorithm="HS256"
            )

            return jsonify({
                "token": token
            })


    @app.route("/api/me", methods=["GET"])
    @token_required
    def me(current_user):
        return jsonify({
            "id": current_user.id,
            "username": current_user.username
        })


    @app.route("/api/events", methods=["GET"])
    @token_required
    def get_events(current_user):
        with SessionLocal() as session:
            result = session.execute(
                select(Event).where(
                    (Event.owner_id == current_user.id)
                    | (Event.visibility == "public")
                )
            )

            events = result.scalars().all()

        return jsonify([
            {
                "id": event.id,
                "owner_id": event.owner_id,
                "title": event.title,
                "icon": event.icon,
                "description": event.description,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat(),
                "visibility": event.visibility
            }
            for event in events
        ])


    @app.route("/api/events/<int:event_id>", methods=["GET"])
    @token_required
    def get_event(current_user, event_id):
        with SessionLocal() as session:
            event = session.execute(
                select(Event).where(
                    (Event.id == event_id)
                    & (
                        (Event.owner_id == current_user.id)
                        | (Event.visibility == "public")
                    )
                )
            ).scalar_one_or_none()
        
        if event is None:
            return jsonify({
                "error": "Event not found"
            }), 404

        return jsonify(
            {
                "id": event.id,
                "owner_id": event.owner_id,
                "title": event.title,
                "icon": event.icon,
                "description": event.description,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat(),
                "visibility": event.visibility
            }
        )


    @app.route("/api/events", methods=["POST"])
    @token_required
    def create_event(current_user):
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

        if data["icon"] not in ALLOWED_ICONS:
            return jsonify({
                "error": "Invalid icon"
            }), 400

        if "visibility" not in data:
            return jsonify({
                "error": "Visibility is required"
            }), 400

        if data["visibility"] not in ["private", "public"]:
            return jsonify({
                "error": "Visibility must be private or public"
            }), 400

        start_at = datetime.fromisoformat(data["start_at"])
        end_at = datetime.fromisoformat(data["end_at"])

        new_event = Event(
            owner_id=current_user.id,
            title=data["title"],
            icon=data["icon"],
            description=data["description"],
            start_at=start_at,
            end_at=end_at,
            visibility=data["visibility"]
        )
        
        with SessionLocal() as session:
            session.add(new_event)
            session.commit()

            return jsonify({
                "id": new_event.id,
                "owner_id": new_event.owner_id,
                "title": new_event.title,
                "icon": new_event.icon,
                "description": new_event.description,
                "start_at": new_event.start_at.isoformat(),
                "end_at": new_event.end_at.isoformat(),
                "visibility": new_event.visibility
            }), 201


    @app.route("/api/events/<int:event_id>", methods=["PUT"])
    @token_required
    def update_event(current_user, event_id):
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

        if data["icon"] not in ALLOWED_ICONS:
            return jsonify({
                "error": "Invalid icon"
            }), 400

        if "visibility" not in data:
            return jsonify({
                "error": "Visibility is required"
            }), 400

        if data["visibility"] not in ["private", "public"]:
            return jsonify({
                "error": "Visibility must be private or public"
            }), 400

        start_at = datetime.fromisoformat(data["start_at"])
        end_at = datetime.fromisoformat(data["end_at"])
        
        with SessionLocal() as session:
            event = session.get(Event, event_id)

            if event is None:
                return jsonify({
                    "error": "Event not found"
                }), 404

            if event.owner_id != current_user.id:
                return jsonify({
                    "error": "You do not have permission to modify this event"
                }), 403

            event.title = data["title"]
            event.icon = data["icon"]
            event.description = data["description"]
            event.start_at = start_at
            event.end_at = end_at
            event.visibility = data["visibility"]

            session.commit()

            return jsonify({
                "id": event.id,
                "title": event.title,
                "icon": event.icon,
                "owner_id": event.owner_id,
                "description": event.description,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat(),
                "visibility": event.visibility
            })


    @app.route("/api/events/<int:event_id>", methods=["DELETE"])
    @token_required
    def delete_event(current_user, event_id):
        with SessionLocal() as session:
            event = session.get(Event, event_id)
        
            if event is None:
                return jsonify({
                    "error": "Event not found"
                }), 404
            
            if event.owner_id != current_user.id:
                return jsonify({
                    "error": "You do not have permission to delete this event"
                }), 403
            
            session.delete(event)
            session.commit()

        return jsonify({
            "message": "Event deleted"
        })
