from api.database.config import Session, engine
from api.schemas.teams import Response, TeamInput, TeamSchema
from api.models.teams import Team
from api.utils.auth_services import get_password_hash, oauth2_scheme, get_current_user
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Team Not Found"}},
)

session = Session(bind=engine)


@router.get(
    "/",
    response_model=list[TeamSchema],
    response_description="Sucesso de resposta da aplicação.",
)
async def getAll(skip: int = 0, limit: int = 100):
    return session.query(Team).offset(skip).limit(limit).all()


@router.get(
    "/{id}",
    response_model=TeamSchema,
    response_description="Sucesso de resposta da aplicação.",
)
async def getById(id: int):
    team = session.query(Team).filter(Team.id == id).first()
    if team == None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post(
    "/create",
    status_code=201,
    response_model=TeamSchema,
    response_description="Sucesso de resposta da aplicação.",
)
async def create(data: TeamInput, token: Annotated[str, Depends(oauth2_scheme)]):
    # Falta fazer as validações para criar o time (acho q nao falta mais)
    team = session.query(Team).filter(Team.name == data.name).first()
    if team != None:
        raise HTTPException(status_code=400, detail="Team with this name already exists")
    hashed_password = get_password_hash(data.password)
    user = await get_current_user(token)
    team_input = Team(name=data.name, password=hashed_password, owner_id=user.id, game_id=data.game_id)
    session.add(team_input)
    session.commit()
    session.refresh(team_input)
    response = {
        "id": team_input.id,
        "name": team_input.name,
        "password": team_input.password,
        "owner_id": team_input.owner_id,
        "game_id": team_input.game_id
    }
    return response

@router.delete(
    "/delete/{id}",
    status_code=200,
    response_model=TeamSchema,
    response_description="Sucesso de resposta da aplicação.",
)
async def delete(id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    user = await get_current_user(token)
    team = session.query(Team).filter(Team.id == id, user.id == Team.owner_id).first()
    if team == None:
        raise HTTPException(status_code=404, detail="Team not found or You aren't the owner of the team")
    
    session.delete(team)
    session.commit()

    return user

