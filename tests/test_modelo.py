import pytest
from flaskr.modelos.modelo import (
    db,
    Roles, RolesEnum,
    Personal,
    Ambulancia, CategoriaAmbulanciaEnum,
    Hospitales
)

def test_crear_rol(db_session):
    rol = Roles(nombre=RolesEnum.ADMINISTRADOR)
    db_session.add(rol)
    db_session.commit()

    assert rol.id is not None
    assert rol.nombre == RolesEnum.ADMINISTRADOR

def test_crear_personal_con_rol(db_session):
    rol = Roles(nombre=RolesEnum.CONDUCTOR)
    db_session.add(rol)
    db_session.commit()

    persona = Personal(
        nombre="Juan Pérez",
        email="juan@example.com",
        personal_rol=RolesEnum.CONDUCTOR
    )
    persona.contrasena = "clave_segura_123"
    db_session.add(persona)
    db_session.commit()

    assert persona.id is not None
    assert persona.verificar_contrasena("clave_segura_123") is True
    assert persona.rol.nombre == RolesEnum.CONDUCTOR

def test_crear_hospital(db_session):
    hospital = Hospitales(
        nombre="Hospital Central",
        direccion="Av. Salud 123",
        capacidad_atencion=120,
        categoria="General"
    )
    db_session.add(hospital)
    db_session.commit()

    assert hospital.id is not None
    assert hospital.nombre == "Hospital Central"
    assert hospital.direccion == "Av. Salud 123"
    assert hospital.capacidad_atencion == 120
    assert hospital.categoria == "General"

def test_crear_ambulancia(db_session):
    hospital = Hospitales(
        nombre="Hospital Regional",
        direccion="Calle 456",
        capacidad_atencion=80,
        categoria="Emergencias"
    )
    db_session.add(hospital)
    db_session.commit()

    ambulancia = Ambulancia(
        placa="XYZ123",
        categoria_ambulancia=CategoriaAmbulanciaEnum.BASICA,
        hospital_id=hospital.id
    )
    db_session.add(ambulancia)
    db_session.commit()

    assert ambulancia.id is not None
    assert ambulancia.placa == "XYZ123"
    assert ambulancia.categoria_ambulancia == CategoriaAmbulanciaEnum.BASICA
    assert ambulancia.hospital_id == hospital.id
