from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from notes.service import InMemoryNoteRepository, NotesService

app = FastAPI(title="Notes API")
service = NotesService(InMemoryNoteRepository())


class NoteInput(BaseModel):
    model_config = ConfigDict(strict=True)
    title: str
    content: str = ""


@app.exception_handler(ValueError)
async def invalid_input(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/notes", status_code=201)
def create_note(data: NoteInput):
    return asdict(service.create(data.title, data.content))


@app.get("/notes")
def list_notes(limit: int = 20, cursor: str | None = None):
    page = service.list_page(limit, cursor)
    return {
        "notes": [asdict(note) for note in page.notes],
        "next_cursor": page.next_cursor,
    }


@app.get("/notes/{note_id}")
def get_note(note_id: str):
    note = service.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Nota non trovata")
    return asdict(note)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    if not service.delete(note_id):
        raise HTTPException(status_code=404, detail="Nota non trovata")
    return Response(status_code=204)
