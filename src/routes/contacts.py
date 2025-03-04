from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=1, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db)
    for contact in contacts:
        contact.birthday = contact.birthday.strftime("%Y-%m-%d")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    contact.birthday = contact.birthday.strftime("%Y-%m-%d")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.create_contact(body, db)
    contact.birthday = contact.birthday.strftime("%Y-%m-%d")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    contact.birthday = contact.birthday.strftime("%Y-%m-%d")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return None


@router.get("/birthdays/", response_model=list[ContactResponse])
async def get_birthdays(limit: int = Query(10, ge=1, le=500), offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_birthdays(limit, offset, db)
    for contact in contacts:
        contact.birthday = contact.birthday.strftime("%Y-%m-%d")
    return contacts

@router.get("/birthdays/", response_model=list[ContactResponse])
async def get_birthdays(limit: int = Query(10, ge=1, le=500), offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_birthdays(limit, offset, db)
    for contact in contacts:

        if isinstance(contact.birthday, datetime.date):
            contact.birthday = contact.birthday.strftime("%Y-%m-%d")
    return contacts


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(query: str = Query(None), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.search_contacts(query, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
