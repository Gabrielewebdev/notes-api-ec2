import os
from dataclasses import asdict

import boto3
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from notes.dynamodb_repository import DynamoDBNoteRepository
from notes.service import InMemoryNoteRepository, NotesService


def build_service():
    backend = os.getenv("NOTES_BACKEND", "memory")

    if backend == "memory":
        return NotesService(InMemoryNoteRepository())

    if backend == "dynamodb":
        table_name = os.getenv("NOTES_TABLE_NAME", "").strip()
        if not table_name:
            raise RuntimeError("NOTES_TABLE_NAME è obbligatorio")

        region = os.getenv("AWS_REGION", "us-east-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        return NotesService(
            DynamoDBNoteRepository(dynamodb.Table(table_name))
        )

    raise RuntimeError(f"NOTES_BACKEND non valido: {backend}")


app = FastAPI(title="Notes API")
service = build_service()


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
