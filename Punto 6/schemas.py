from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ==========================================
# ESQUEMAS CRUD (Del Punto 4 y 5)
# ==========================================

class LugarBase(BaseModel):
    nombre: str
    direccion: str

class LugarCreate(LugarBase):
    pass

class LugarOut(LugarBase):
    id: int
    class Config:
        from_attributes = True

class SectorBase(BaseModel):
    nombre: str
    capacidad_maxima: int
    lugar_id: int

class SectorCreate(SectorBase):
    pass

class SectorOut(SectorBase):
    id: int
    class Config:
        from_attributes = True

class EventoBase(BaseModel):
    nombre: str
    fecha: str
    lugar_id: int

class EventoCreate(EventoBase):
    pass

class EventoOut(EventoBase):
    id: int
    class Config:
        from_attributes = True

# ==========================================
# ESQUEMAS HISTORIAS DE USUARIO (Del Punto 6)
# ==========================================

class CotizacionRequest(BaseModel):
    evento_id: int
    sector_id: int
    cantidad: int

class CotizacionResponse(BaseModel):
    subtotal: float
    mensaje: str

class PagoRequest(BaseModel):
    entradas_ids: List[int]
    total_cotizado: float
    numero_tarjeta: str

class PagoResponse(BaseModel):
    mensaje: str
    venta_id: int
    estado_entradas: str

class EscanearRequest(BaseModel):
    codigo_qr: str

class AccesoResponse(BaseModel):
    mensaje: str
    estado_ticket: str
    hora_ingreso: Optional[datetime] = None