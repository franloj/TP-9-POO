from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db  # Dependencia real activada
import models
import schemas
from services import CotizacionService, PagoService

router = APIRouter(tags=["SmartTicket TP9"])

# ==========================================
# ENDPOINTS CRUD BÁSICOS (Del Punto 4)
# ==========================================

@router.post("/lugares/", response_model=schemas.LugarOut, tags=["CRUD Base"])
def crear_lugar(lugar: schemas.LugarCreate, db: Session = Depends(get_db)):
    db_lugar = models.Lugar(nombre=lugar.nombre, direccion=lugar.direccion)
    db.add(db_lugar)
    db.commit()
    db.refresh(db_lugar)
    return db_lugar

@router.get("/lugares/", response_model=List[schemas.LugarOut], tags=["CRUD Base"])
def listar_lugares(db: Session = Depends(get_db)):
    return db.query(models.Lugar).all()

@router.post("/sectores/", response_model=schemas.SectorOut, tags=["CRUD Base"])
def crear_sector(sector: schemas.SectorCreate, db: Session = Depends(get_db)):
    db_sector = models.Sector(
        nombre=sector.nombre, 
        capacidad_maxima=sector.capacidad_maxima, 
        lugar_id=sector.lugar_id
    )
    db.add(db_sector)
    db.commit()
    db.refresh(db_sector)
    return db_sector

@router.get("/sectores/", response_model=List[schemas.SectorOut], tags=["CRUD Base"])
def listar_sectores(db: Session = Depends(get_db)):
    return db.query(models.Sector).all()

@router.post("/eventos/", response_model=schemas.EventoOut, tags=["CRUD Base"])
def crear_evento(evento: schemas.EventoCreate, db: Session = Depends(get_db)):
    db_evento = models.Evento(
        nombre=evento.nombre, 
        fecha=evento.fecha, 
        lugar_id=evento.lugar_id
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.get("/eventos/", response_model=List[schemas.EventoOut], tags=["CRUD Base"])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(models.Evento).all()

# ==========================================
# HISTORIAS DE USUARIO (Del Punto 6)
# ==========================================

@router.post("/api/v1/cotizar", response_model=schemas.CotizacionResponse, tags=["HU 1 - Cotización"])
def cotizar_entradas(peticion: schemas.CotizacionRequest, db: Session = Depends(get_db)):
    servicio = CotizacionService(db)
    return servicio.cotizar(peticion)

@router.post("/api/v1/iniciar-pago", response_model=schemas.PagoResponse, tags=["HU 2 - Pagos"])
def iniciar_pago(request: schemas.PagoRequest, db: Session = Depends(get_db)):
    servicio = PagoService(db)
    return servicio.procesar_pago(request)

@router.post("/api/v1/escanear", response_model=schemas.AccesoResponse, tags=["HU 3 - Control de Acceso"])
def escanear_acceso(request: schemas.EscanearRequest, db: Session = Depends(get_db)):
    entrada = db.query(models.Entrada).filter(models.Entrada.codigo_qr == request.codigo_qr).first()
    
    if not entrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ticket Inválido o Inexistente"
        )

    try:
        entrada.registrar_ingreso()
        
        db.commit()
        db.refresh(entrada)
        
        return schemas.AccesoResponse(
            mensaje="Acceso Permitido",
            estado_ticket=entrada.estado,
            hora_ingreso=entrada.hora_ingreso
        )

    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Entrada ya utilizada":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)