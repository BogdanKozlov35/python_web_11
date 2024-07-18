from fastapi import HTTPException, Depends, Query
from sqlalchemy import select, delete, or_, join
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from src.entity.models import Contact, Email, Phone
from src.database.db import get_db
from src.schemas.contact import ContactResponse, ContactSchema, ContactUpdateSchema


async def handle_exception(e, db):
    print(f"Error: {e}")
    await db.rollback()
    raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_contacts(limit: int, offset: int, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Contact).offset(offset).limit(limit)
        result = await db.execute(stmt)
        contacts = result.scalars().all()
        for contact in contacts:
            await db.refresh(contact, ['emails', 'phones'])
        return contacts
    except Exception as e:
        await handle_exception(e, db)


async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Contact).filter_by(id=contact_id)
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        await db.refresh(contact, ['emails', 'phones'])
        return contact
    except Exception as e:
        await handle_exception(e, db)


async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    try:
        contact = Contact(
            firstname=body.firstname,
            lastname=body.lastname,
            birthday=body.birthday,
            description=body.description
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)

        if body.emails:
            for email_data in body.emails:
                email = Email(email=email_data.email, contact_id=contact.id)
                db.add(email)
        if body.phones:
            for phone_data in body.phones:
                phone = Phone(phone=phone_data.phone, contact_id=contact.id)
                db.add(phone)

        await db.commit()
        await db.refresh(contact, ['emails', 'phones'])
        return contact
    except Exception as e:
        await handle_exception(e, db)


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Contact).filter_by(id=contact_id)
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()

        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")

        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.birthday = body.birthday
        contact.description = body.description

        if body.emails is not None:
            await db.execute(delete(Email).where(Email.contact_id == contact_id))
            for email_data in body.emails:
                email = Email(email=email_data.email, contact_id=contact.id)
                db.add(email)

        if body.phones is not None:
            await db.execute(delete(Phone).where(Phone.contact_id == contact_id))
            for phone_data in body.phones:
                phone = Phone(phone=phone_data.phone, contact_id=contact.id)
                db.add(phone)

        await db.commit()
        await db.refresh(contact, ['emails', 'phones'])
        return contact
    except Exception as e:
        await handle_exception(e, db)


async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Contact).filter_by(id=contact_id)
        result = await db.execute(stmt)
        contact = result.scalar_one_or_none()

        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")

        await db.execute(delete(Email).where(Email.contact_id == contact_id))
        await db.execute(delete(Phone).where(Phone.contact_id == contact_id))
        await db.delete(contact)
        await db.commit()

        return contact
    except Exception as e:
        await handle_exception(e, db)


async def get_birthdays(limit: int, offset: int, db: AsyncSession = Depends(get_db)):
    try:
        today = datetime.now().date()
        future_date = today + timedelta(days=7)

        async with db.begin() as tx:
            stmt = select(Contact).filter(Contact.birthday.between(today, future_date)).offset(offset).limit(limit)
            result = await db.execute(stmt)
            contacts = result.scalars().all()

            for contact in contacts:
                await db.refresh(contact, ['emails', 'phones'])

        return contacts

    except Exception as e:
        await handle_exception(e, db)

async def search_contacts(query: str, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Contact).filter(or_(
            Contact.firstname.ilike(f"%{query}%"),
            Contact.lastname.ilike(f"%{query}%"),
            Contact.emails.any(Email.email.ilike(f"%{query}%")),
            Contact.phones.any(Phone.phone.ilike(f"%{query}%"))
        ))
        result = await db.execute(stmt)
        contacts = result.scalars().all()

        for contact in contacts:
            await db.refresh(contact, ['emails', 'phones'])

        return contacts
    except Exception as e:
        await handle_exception(e, db)


