from fastapi import APIRouter, HTTPException, Response, status

from app import storage
from app.schemas import Club, ClubCreate, ClubUpdate, ErrorResponse, Room

router = APIRouter(prefix="/api", tags=["Справочники"])

NOT_FOUND_CLUB = {404: {"model": ErrorResponse, "description": "Клуб не найден"}}
CONFLICT_CLUB = {409: {"model": ErrorResponse, "description": "Клуб с таким названием уже существует или имеет мероприятия"}}


@router.get("/clubs", response_model=list[Club], summary="Список клубов")
def list_clubs():
    """Возвращает список всех зарегистрированных клубов."""
    return list(storage.CLUBS.values())


@router.get(
    "/clubs/{club_id}",
    response_model=Club,
    responses=NOT_FOUND_CLUB,
    summary="Один клуб",
)
def get_club(club_id: int):
    """Возвращает данные клуба по id."""
    club = storage.CLUBS.get(club_id)
    if club is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Клуб не найден")
    return club


@router.post(
    "/clubs",
    response_model=Club,
    status_code=status.HTTP_201_CREATED,
    responses=CONFLICT_CLUB,
    summary="Создать клуб",
)
def create_club(payload: ClubCreate):
    """
    Создаёт новый клуб.
    Название должно быть уникальным без учёта регистра (иначе 409 Conflict).
    """
    name_lower = payload.name.lower()
    for existing in storage.CLUBS.values():
        if existing["name"].lower() == name_lower:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Клуб с названием «{payload.name}» уже существует",
            )

    new_id = storage.next_club_id()
    new_club = {"id": new_id, "name": payload.name}
    storage.CLUBS[new_id] = new_club
    return new_club


@router.patch(
    "/clubs/{club_id}",
    response_model=Club,
    responses={**NOT_FOUND_CLUB, **CONFLICT_CLUB},
    summary="Переименовать клуб",
)
def update_club(club_id: int, payload: ClubUpdate):
    """
    Переименовывает клуб.
    Новое название должно быть уникальным среди других клубов без учёта регистра.
    """
    club = storage.CLUBS.get(club_id)
    if club is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Клуб не найден")

    name_lower = payload.name.lower()
    for other_id, other_club in storage.CLUBS.items():
        if other_id != club_id and other_club["name"].lower() == name_lower:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Клуб с названием «{payload.name}» уже существует",
            )

    club["name"] = payload.name
    return club


@router.delete(
    "/clubs/{club_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**NOT_FOUND_CLUB, **CONFLICT_CLUB},
    summary="Удалить клуб",
)
def delete_club(club_id: int):
    """
    Удаляет клуб.
    Если у клуба есть мероприятия — возвращает 409 Conflict с указанием их количества.
    """
    if club_id not in storage.CLUBS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Клуб не найден")

    events_count = sum(1 for e in storage.EVENTS.values() if e.get("club_id") == club_id)
    if events_count > 0:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Нельзя удалить клуб: у него запланировано мероприятий: {events_count}",
        )

    del storage.CLUBS[club_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/rooms", response_model=list[Room], summary="Список аудиторий")
def list_rooms():
    """Возвращает список всех аудиторий."""
    return list(storage.ROOMS.values())