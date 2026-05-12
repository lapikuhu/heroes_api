Backend:

cd app
uvicorn main:app --reload

http://127.0.0.1:8000
http://127.0.0.1:8000/docs


Users employ a defense in depth pattern: services authenticate as well.
All other features are shallow, with routes taking care of acccess control independently.

Users can have multiple roles.

Tests from the repo root:

Frontend:

cd frontend
npm install
npm run dev

http://127.0.0.1:5173

No npm fallback on Windows:

cd frontend
py -m http.server 5173

Open http://127.0.0.1:5173/standalone.html
