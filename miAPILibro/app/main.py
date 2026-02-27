from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import datetime

app = FastAPI(
    title="API de Gestión de Biblioteca",
    description="Artemio Hurtado Hernandez",
    version="1.0"
)

class EstadoLibro(str, Enum):
    disponible = "disponible"
    prestado = "prestado"

libros = [
    {"id": 1, "titulo": "El principito", "estado": "disponible", "paginas": 96, "id_usuario": 1, "año": 1943}
]

Usuarios = [
    {"id": 1, "nombre": "Artemio Hurtado", "correo": "artemiohurtadohdz2784@gmail.com"}
]

class CrearUsuario(BaseModel):    
    id: int = Field(..., gt=0)
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico válido")

class CrearLibro(BaseModel):
    id: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=2, max_length=100, description="Título del libro")
    estado: EstadoLibro = Field(..., description="Estado del libro")
    paginas: int = Field(..., gt=1, description="Número de páginas")
    id_usuario: int = Field(..., gt=0, description="ID del usuario que tiene el libro")
    año: int = Field(..., gt=1450, le=datetime.now().year, description=f"Año de publicación (mayor a 1450 y menor o igual a {datetime.now().year})")

@app.put("/v1/libros/", tags=['Libros'])
async def actualizar_libro(libro: CrearLibro):
    usuario_encontrado = False
    for usr in Usuarios:
        if usr["id"] == libro.id_usuario:
            usuario_encontrado = True
            break
    
    if not usuario_encontrado:
        raise HTTPException(
            status_code=404,
            detail="El usuario con ese ID no existe"
        )
    
    for lib in libros:
        if lib["id"] == libro.id:
            lib["titulo"] = libro.titulo
            lib["estado"] = libro.estado
            lib["paginas"] = libro.paginas
            lib["id_usuario"] = libro.id_usuario
            lib["año"] = libro.año

            return {
                "Mensaje": "Libro actualizado",
                "Libro": lib,
                "status": "200"
            }

    raise HTTPException(
        status_code=404,
        detail="El libro con ese ID no existe"
    )


@app.get("/v1/libros/disponibles/", tags=['Libros'])
async def listar_libros_disponibles():
    libros_disponibles = []
    for lib in libros:
        if lib["estado"] == "disponible":
            libros_disponibles.append(lib)
    
    return{
        "status": "200",
        "total": len(libros_disponibles),
        "libros": libros_disponibles
    }

@app.get("/v1/libros/", tags=['Libros'])
async def listar_todos_libros():
    return{
        "status": "200",
        "total": len(libros),
        "libros": libros
    }

@app.get("/v1/libros/buscar/", tags=['Libros'])
async def buscar_libro_por_nombre(titulo: str):
    libros_encontrados = []
    for lib in libros:
        if titulo.lower() in lib["titulo"].lower():
            libros_encontrados.append(lib)
    
    if not libros_encontrados:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron libros con el título '{titulo}'"
        )
    
    return{
        "status": "200",
        "total": len(libros_encontrados),
        "libros": libros_encontrados
    }

@app.post("/v1/libros/", status_code=201, tags=['Libros'])
async def agregar_libro(libro: CrearLibro):
    for lib in libros:
        if lib["id"] == libro.id:
            raise HTTPException(
                status_code=400, 
                detail="El id ya existe"
            )
    
    libros.append(libro.model_dump())
    return{
        "Mensaje": "Libro agregado",
        "Libro": libro,
        "status": "201"
    }

@app.post("/v1/usuarios/", tags=['Usuarios'])
async def agregar_usuario(usuario: CrearUsuario):
    for usr in Usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400, 
                detail="El id ya existe"
            )
    
    Usuarios.append(usuario.model_dump())
    return{
        "Mensaje": "Usuario agregado",
        "Usuario": usuario,
        "status": "200"
    }

@app.post("/v1/libros/{libro_id}/prestar/", tags=['Libros'])
async def prestar_libro(libro_id: int, id_usuario: int):
    usuario_encontrado = False
    for usr in Usuarios:
        if usr["id"] == id_usuario:
            usuario_encontrado = True
            break
    
    if not usuario_encontrado:
        raise HTTPException(
            status_code=404,
            detail="El usuario con ese ID no existe"
        )
    
    for lib in libros:
        if lib["id"] == libro_id:
            if lib["estado"] != "disponible":
                raise HTTPException(
                    status_code=409,
                    detail=f"El libro '{lib['titulo']}' ya está prestado"
                )
            
            lib["estado"] = "prestado"
            lib["id_usuario"] = id_usuario
            
            return {
                "Mensaje": "Préstamo registrado exitosamente",
                "Libro": lib,
                "status": "200"
            }
    
    raise HTTPException(
        status_code=404,
        detail="El libro con ese ID no existe"
    )

@app.post("/v1/libros/{libro_id}/devolver/", tags=['Libros'])
async def devolver_libro(libro_id: int):
    for lib in libros:
        if lib["id"] == libro_id:
            if lib["estado"] != "prestado":
                raise HTTPException(
                    status_code=409,
                    detail=f"El registro de préstamo no existe. El libro '{lib['titulo']}' no está prestado"
                )
            
            lib["estado"] = "disponible"
            
            return {
                "Mensaje": "Libro devuelto exitosamente",
                "Libro": lib,
                "status": "200"
            }
    
    raise HTTPException(
        status_code=404,
        detail="El libro con ese ID no existe"
    )

@app.delete("/v1/libros/{libro_id}/", tags=['Libros'])
async def eliminar_libro(libro_id: int):
    for i, lib in enumerate(libros):
        if lib["id"] == libro_id:
            libro_eliminado = libros.pop(i)
            
            return {
                "Mensaje": "Libro eliminado exitosamente",
                "Libro": libro_eliminado,
                "status": "200"
            }
    
    raise HTTPException(
        status_code=404,
        detail="El libro con ese ID no existe"
    )

"""
==============================================
LISTADO DE RUTAS Y FUNCIONES DE LA API
==============================================

ENDPOINTS DE LIBROS:
--------------------
PUT    /v1/libros/                          - actualizar_libro()          - Actualizar libro completo
GET    /v1/libros/disponibles/              - listar_libros_disponibles() - Listar solo libros disponibles
GET    /v1/libros/                          - listar_todos_libros()       - Listar todos los libros
GET    /v1/libros/buscar/?titulo={texto}    - buscar_libro_por_nombre()   - Buscar libros por título
POST   /v1/libros/                          - agregar_libro()             - Registrar nuevo libro (201)
POST   /v1/libros/{libro_id}/prestar/       - prestar_libro()             - Prestar libro a usuario
POST   /v1/libros/{libro_id}/devolver/      - devolver_libro()            - Devolver libro prestado
DELETE /v1/libros/{libro_id}/               - eliminar_libro()            - Eliminar libro del sistema

ENDPOINTS DE USUARIOS:
---------------------
POST   /v1/usuarios/                        - agregar_usuario()           - Registrar nuevo usuario

CÓDIGOS DE ESTADO HTTP:
-----------------------
200 - OK: Operación exitosa
201 - Created: Recurso creado exitosamente
400 - Bad Request: Datos inválidos o ID duplicado
404 - Not Found: Recurso no encontrado
409 - Conflict: Conflicto (libro ya prestado o sin préstamo activo)
"""
