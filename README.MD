cd app
uvicorn main:app --reload

http://127.0.0.1:8000
http://127.0.0.1:8000/docs


Users employ a defense in depth pattern: services authenticate as well.
All other features are shallow, with routes taking care of acccess control independently.

Users can have multiple roles.

pytest tests/ -v