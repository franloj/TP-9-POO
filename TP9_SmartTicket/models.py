from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Lugar(Base):
    __tablename__ = "lugares"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)

    sectores = relationship("Sector", back_populates="lugar")
    eventos = relationship("Evento", back_populates="lugar")

class Sector(Base):
    __tablename__ = "sectores"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    capacidad_maxima = Column(Integer, nullable=False)
    lugar_id = Column(Integer, ForeignKey("lugares.id"))

    lugar = relationship("Lugar", back_populates="sectores")
    entradas = relationship("Entrada", back_populates="sector")

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    fecha = Column(String, nullable=False)
    lugar_id = Column(Integer, ForeignKey("lugares.id"))

    lugar = relationship("Lugar", back_populates="eventos")
    entradas = relationship("Entrada", back_populates="evento")

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    ventas = relationship("Venta", back_populates="cliente")

class Entrada(Base):
    __tablename__ = "entradas"
    id = Column(Integer, primary_key=True, index=True)
    codigo_qr = Column(String, unique=True, index=True, nullable=True)
    estado = Column(String, nullable=False, default="Disponible")
    hora_ingreso = Column(DateTime, nullable=True)
    
    sector_id = Column(Integer, ForeignKey("sectores.id"))
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True)

    sector = relationship("Sector", back_populates="entradas")
    evento = relationship("Evento", back_populates="entradas")
    venta = relationship("Venta", back_populates="entradas")

    # GRASP: Experto en Información - La entidad gestiona su propio estado
    def registrar_ingreso(self):
        if self.estado == "Utilizada":
            raise ValueError("Entrada ya utilizada")
        
        if self.estado in ["Reservada", "Disponible"]:
            raise ValueError("Ticket no emitido / Falta de pago")
            
        if self.estado == "Emitida":
            self.estado = "Utilizada"
            self.hora_ingreso = datetime.now()
        else:
            raise ValueError("Estado de ticket desconocido")

class Venta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    estado = Column(String, nullable=False, default="Pendiente")
    tarjeta = Column(String, nullable=False)
    
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)

    cliente = relationship("Cliente", back_populates="ventas")
    entradas = relationship("Entrada", back_populates="venta")

    # GRASP: Experto en Información
    def confirmar_pago(self, pasarela_aprobada: bool):
        if not pasarela_aprobada:
            self.estado = "Cancelada"
            raise ValueError("Pago denegado")
        self.estado = "Pagada"