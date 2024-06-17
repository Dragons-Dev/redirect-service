from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

import sqlite3


SECRET_KEY = "SOME_SUPER_SECURE_SECRET"


class Redirect(BaseModel):
    name: str
    value: str
    secret: str


with sqlite3.connect("redirects.db") as db:
    db.execute("CREATE TABLE IF NOT EXISTS redirects (name TEXT PRIMARY KEY, value TEXT)")


app = FastAPI()


@app.get("/{redirect_name}")
def redirect(redirect_name: str):
    with sqlite3.connect("redirects.db") as db:
        try:
            _, value = db.execute("SELECT * FROM redirects WHERE name = ?", (redirect_name,)).fetchone()
        except TypeError:
            return JSONResponse({"error": f"No redirect named '{redirect_name}'."}, 404)
    return RedirectResponse(value, 303)


@app.get("/api/get_redirect/{redirect}")
def get_redirect(redirect: str):
    with sqlite3.connect("redirects.db") as db:
        try:
            _, value = db.execute("SELECT * FROM redirects WHERE name = ?", (redirect,)).fetchone()
            return JSONResponse({"success": f"domain.tld/{redirect} redirects to '{value}'."}, 200)
        except TypeError:
            return JSONResponse({"error": f"domain.tld/{redirect} is not defined."}, 400)


@app.get("/api/get_all_redirects")
def get_all_redirects():
    with sqlite3.connect("redirects.db") as db:
        try:
            x = db.execute("SELECT * FROM redirects").fetchall()
            response = {}
            for entry in x:
                response[str(entry[0])] = entry[1]
            return JSONResponse({"success": response}, 200)
        except TypeError:
            return JSONResponse({"error": f"domain.tld/{redirect} is not defined."}, 400)


@app.post("/api/add_redirect")
def add_redirect(redirect: Redirect):
    if redirect.secret != SECRET_KEY:
        return JSONResponse({"error": f"Invalid secret key"}, 401)
    with sqlite3.connect("redirects.db") as db:
        try:
            _, value = db.execute("SELECT * FROM redirects WHERE name = ?", (redirect.name,)).fetchone()
            if value:
                return JSONResponse({"error": f"'{redirect.name}' already defined as '{value}'."}, 400)
        except TypeError:
            db.execute("INSERT INTO redirects VALUES (?,?)", (redirect.name, redirect.value))
            db.commit()
            return JSONResponse(
                {"success": f"domain.tld/{redirect.name} now redirects to '{redirect.value}'."},
                200,
            )


@app.put("/api/update_redirect/{redirect_name}")
def update_redirect(redirect_name: str, redirect: Redirect):
    if redirect.secret != SECRET_KEY:
        return JSONResponse({"error": f"Invalid secret key"}, 401)
    with sqlite3.connect("redirects.db") as db:
        try:
            _, value = db.execute("SELECT * FROM redirects WHERE name = ?", (redirect_name,)).fetchone()
            db.execute(
                "UPDATE redirects SET value = ? WHERE name = ?",
                (redirect.value, redirect_name),
            )
            db.commit()
            return JSONResponse(
                {"success": f"domain.tld/{redirect.name} now redirects to '{redirect.value}'."},
                200,
            )
        except TypeError:
            return JSONResponse({"error": f"domain.tld/{redirect.name} is not defined."}, 400)


@app.delete("/api/remove_redirect")
def remove_redirect(redirect: Redirect):
    if redirect.secret != SECRET_KEY:
        return JSONResponse({"error": f"Invalid secret key"}, 401)
    with sqlite3.connect("redirects.db") as db:
        try:
            _, value = db.execute("SELECT * FROM redirects WHERE name = ?", (redirect.name,)).fetchone()
            x = db.execute("DELETE from redirects where name = ?", (redirect.name,))
            db.commit()
            return JSONResponse({"success": f"domain.tld/{redirect.name} is now free."}, 200)
        except TypeError:
            return JSONResponse({"error": f"domain.tld/{redirect.name} is not defined."}, 400)


if __name__ == "__main__":
    uvicorn.run("redirect_server:app")
