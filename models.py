from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gestionpro.db")
# Railway usa postgres:// pero SQLAlchemy necesita postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(200))
    rol = Column(String(20), default="vendedor")  # admin, vendedor
    activo = Column(Boolean, default=True)
    creado = Column(DateTime, default=datetime.utcnow)

class Familia(Base):
    __tablename__ = "familias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    descripcion = Column(String(200), nullable=True)

class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150))
    cuit = Column(String(20), nullable=True)
    telefono = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    contacto = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)
    productos = relationship("Producto", back_populates="proveedor")

class Impuesto(Base):
    __tablename__ = "impuestos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50))   # IVA 21%, IVA 10.5%, IIBB, etc.
    porcentaje = Column(Float)
    activo = Column(Boolean, default=True)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True)
    codigo_barra = Column(String(100), nullable=True, index=True)
    descripcion = Column(String(300))
    familia_id = Column(Integer, ForeignKey("familias.id"), nullable=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    costo = Column(Float, default=0)
    lista1 = Column(Float, default=0)
    lista2 = Column(Float, default=0)
    lista3 = Column(Float, default=0)
    lista4 = Column(Float, default=0)
    impuesto_id = Column(Integer, ForeignKey("impuestos.id"), nullable=True)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=1)
    compra_minima = Column(Integer, default=1)
    unidad = Column(String(20), default="unidad")
    activo = Column(Boolean, default=True)
    fecha_alta = Column(DateTime, default=datetime.utcnow)
    proveedor = relationship("Proveedor", back_populates="productos")
    familia = relationship("Familia")
    impuesto = relationship("Impuesto")

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150))
    cuit = Column(String(20), nullable=True)
    telefono = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    condicion_iva = Column(String(50), default="Consumidor Final")
    lista_precio = Column(String(10), default="lista1")
    saldo_cc = Column(Float, default=0)
    activo = Column(Boolean, default=True)

class Comprobante(Base):
    __tablename__ = "comprobantes"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer)
    tipo = Column(String(30))       # Factura A/B/C, Remito, Presupuesto
    fecha = Column(DateTime, default=datetime.utcnow)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    cliente_nombre = Column(String(150))
    items = Column(JSON)            # [{prod_id, codigo, desc, qty, precio, imp_pct}]
    subtotal = Column(Float, default=0)
    descuento_pct = Column(Float, default=0)
    descuento_val = Column(Float, default=0)
    impuestos_val = Column(Float, default=0)
    total = Column(Float, default=0)
    lista_precio = Column(String(10), default="lista1")
    forma_pago = Column(String(50), default="Efectivo")
    estado = Column(String(20), default="Pendiente")  # Pendiente, Pagado, Anulado
    observaciones = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    impuestos_detalle = Column(JSON, nullable=True)  # [{nombre, pct, base, valor}]

class Movimiento(Base):
    __tablename__ = "movimientos"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String(30))       # Ingreso, Egreso, Venta, Ajuste
    producto_id = Column(Integer, ForeignKey("productos.id"))
    producto_codigo = Column(String(50))
    producto_desc = Column(String(200))
    cantidad = Column(Integer)
    stock_anterior = Column(Integer)
    stock_nuevo = Column(Integer)
    motivo = Column(String(200), nullable=True)
    referencia_id = Column(Integer, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

class OrdenCompra(Base):
    __tablename__ = "ordenes_compra"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer)
    fecha = Column(DateTime, default=datetime.utcnow)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    proveedor_nombre = Column(String(150))
    items = Column(JSON)            # [{prod_id, codigo, desc, qty, costo}]
    total = Column(Float, default=0)
    estado = Column(String(20), default="Borrador")  # Borrador, Enviada, Recibida, Cancelada
    observaciones = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

class Configuracion(Base):
    __tablename__ = "configuracion"
    id = Column(Integer, primary_key=True)
    clave = Column(String(100), unique=True)
    valor = Column(Text)

def create_tables():
    Base.metadata.create_all(bind=engine)
