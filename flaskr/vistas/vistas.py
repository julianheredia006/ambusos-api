from flask import request
from flask_restful import Resource
from sqlalchemy.orm import joinedload
from ..modelos import db,AsignacionAmbulancia,AsignacionAmbulanciaSchema, Roles, RolesSchema, Ambulancia, Personal, FormularioAccidente, ReporteViajes, AmbulanciaSchema, PersonalSchema, FormularioAccidenteSchema, ReporteViajesSchema, Hospitales, HospitalSchema
from ..modelos import RolesEnum
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity
)
# Esquemas para serializar los datos
asignacion_ambulancia_schema = AsignacionAmbulanciaSchema()
asignaciones_ambulancia_schema = AsignacionAmbulanciaSchema(many=True)
hospital_schema = HospitalSchema()
hospitales_schema = HospitalSchema(many=True)
ambulancia_schema = AmbulanciaSchema()
ambulancias_schema = AmbulanciaSchema(many=True)
personal_schema = PersonalSchema()
personales_schema = PersonalSchema(many=True)
formulario_accidente_schema = FormularioAccidenteSchema()
formulario_accidente_schema = FormularioAccidenteSchema(many=True)
reporte_viajes_schema = ReporteViajesSchema()
reportes_viajes_schema = ReporteViajesSchema(many=True)



import logging

from flask import request
from flask_restx import Resource
from sqlalchemy.orm.exc import NoResultFound

import logging
import traceback
from flask_restx import Resource
from flask import request
from sqlalchemy.exc import IntegrityError
from flaskr.modelos.modelo import db, Personal, Roles  # Asegúrate de importar Roles correctamente
from sqlalchemy import func  # 👈 Asegúrate de tener esto 
from sqlalchemy import cast, String 
class VistaSignin(Resource):
    def post(self):
        try:
            nombre_Personal = request.json.get("nombre")
            email_Personal = request.json.get("email")
            contrasena_Personal = request.json.get("contrasena")
            rol_nombre = request.json.get("personal_rol")

            if not nombre_Personal or not email_Personal or not contrasena_Personal:
                return {"mensaje": "Nombre, email y contraseña son obligatorios."}, 400

            if Personal.query.filter_by(nombre=nombre_Personal).first():
                return {"mensaje": "El nombre de usuario ya está registrado"}, 409

            if Personal.query.filter_by(email=email_Personal).first():
                return {"mensaje": "El correo electrónico ya está registrado"}, 409

            rol = None
            if rol_nombre:
                # 🔥 Convertimos enum a texto para poder aplicar ILIKE correctamente
                rol = Roles.query.filter(cast(Roles.nombre, String).ilike(rol_nombre)).first()
                if not rol:
                    return {"mensaje": f"El rol '{rol_nombre}' no existe."}, 404

            nuevo_Personal = Personal(
                nombre=nombre_Personal,
                email=email_Personal,
                personal_rol=rol.nombre if rol else None,
            )
            nuevo_Personal.contrasena = contrasena_Personal

            db.session.add(nuevo_Personal)
            db.session.commit()

            return {"mensaje": "Usuario creado exitosamente. Ahora puede iniciar sesión."}, 201

        except ValueError as e:
            traceback.print_exc()
            return {"mensaje": str(e)}, 400

        except IntegrityError as e:
            traceback.print_exc()
            db.session.rollback()
            return {"mensaje": "Error de integridad. Verifica los datos ingresados."}, 500

        except Exception as e:
            traceback.print_exc()
            return {"mensaje": f"Error inesperado en el servidor: {str(e)}"}, 500
class VistalogIn(Resource):
    def post(self):
        # Obtener credenciales del usuario
        nombre = request.json.get("nombre")
        contrasena = request.json.get("contrasena")

        # Validar que se hayan proporcionado las credenciales
        if not nombre or not contrasena:
            return {"mensaje": "El nombre y la contraseña son obligatorios."}, 400

        # Buscar al usuario por nombre (haciendo la comparación insensible a mayúsculas)
        usuario = Personal.query.filter(Personal.nombre.ilike(nombre)).first()

        # Verificar credenciales
        if usuario and usuario.verificar_contrasena(contrasena):
            # Generar token de acceso
            token_de_acceso = create_access_token(identity=str(usuario.id))

            # Devolver mensaje exitoso con el token, el rol y el id del usuario
            return {
                "mensaje": "Inicio de sesión exitoso",
                "token": token_de_acceso,
                "rol": usuario.personal_rol.value,  # Convertimos el Enum a su valor
                "id": usuario.id,  # Agregar el ID del usuario a la respuesta
                "nombre_usuario": usuario.nombre  # Opcional, para enviar también el nombre
            }, 200

        # Respuesta en caso de credenciales incorrectas
        return {"mensaje": "Usuario o contraseña incorrectos"}, 401
    
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..modelos import Personal

class VistaProtegida(Resource):
    @jwt_required()
    def get(self):
        # Obtener el ID del usuario desde el token JWT
        usuario_id = get_jwt_identity()

        # Buscar al usuario por su ID
        usuario = Personal.query.get(usuario_id)
        if not usuario:
            return {"mensaje": "Usuario no encontrado"}, 404

        # Devolver la información del usuario
        return {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rol": usuario.personal_rol.value
        }, 200


class VistaPersonal(Resource):
    
    def get(self):
        """Obtener todos los registros de personal"""
        personales = Personal.query.all()
        return personales_schema.dump(personales), 200

    def post(self):
        """Crear un nuevo personal"""
        # Obtener el rol de la solicitud, si existe
        rol_nombre = request.json.get('rol', None)
        rol = Roles.query.filter_by(nombre=rol_nombre).first() if rol_nombre else None
        
        # Crear nuevo objeto Personal
        nuevo_personal = Personal(
            nombre=request.json['nombre'],
            email=request.json['email'],
            contrasena=request.json['contrasena'],
            personal_rol=rol.nombre if rol else None  # Asignar el rol por nombre
        )
        
        # Añadir y guardar en la base de datos
        db.session.add(nuevo_personal)
        db.session.commit()

        return personal_schema.dump(nuevo_personal), 201

    def put(self, id):
        """Actualizar un personal existente"""
        personal = Personal.query.get(id)
        
        if not personal:
            return {"mensaje": "Usuario no encontrado."}, 404

        # Actualizar los datos del personal
        personal.nombre = request.json.get('nombre', personal.nombre)
        personal.email = request.json.get('email', personal.email)
        
        # Actualizar el rol, si se ha enviado uno en la solicitud
        rol_nombre = request.json.get('rol', None)
        if rol_nombre:
            rol = Roles.query.filter_by(nombre=rol_nombre).first()
            personal.personal_rol = rol.nombre if rol else None
        
        # Guardar los cambios en la base de datos
        db.session.commit()

        return personal_schema.dump(personal), 200

    def delete(self, id):
        """Eliminar un personal por su ID"""
        personal = Personal.query.get(id)
        
        if not personal:
            return {"mensaje": "Usuario no encontrado."}, 404

        # Eliminar de la base de datos
        db.session.delete(personal)
        db.session.commit()

        return {"mensaje": "Usuario eliminado."}, 204
class VistaAmbulancias(Resource):
    def get(self):
        # Incluye el hospital relacionado
        ambulancias = Ambulancia.query.options(joinedload(Ambulancia.hospital)).all()
        return ambulancias_schema.dump(ambulancias), 200

    def post(self):
        nueva_ambulancia = Ambulancia(
            placa=request.json['placa'],
            categoria_ambulancia=request.json['categoria_ambulancia'],
            hospital_id=request.json.get('hospital_id')
        )
        db.session.add(nueva_ambulancia)
        db.session.commit()
        return ambulancia_schema.dump(nueva_ambulancia), 201

    def put(self, id):
        ambulancia = Ambulancia.query.get(id)
        if not ambulancia:
            return {"mensaje": "Ambulancia no encontrada."}, 404

        ambulancia.placa = request.json.get('placa', ambulancia.placa)
        ambulancia.categoria_ambulancia = request.json.get('categoria_ambulancia', ambulancia.categoria_ambulancia)
        ambulancia.hospital_id = request.json.get('hospital_id', ambulancia.hospital_id)
        db.session.commit()
        return ambulancia_schema.dump(ambulancia), 200

    def delete(self, id):
        ambulancia = Ambulancia.query.get(id)
        if not ambulancia:
            return {"mensaje": "Ambulancia no encontrada."}, 404

        db.session.delete(ambulancia)
        db.session.commit()
        return {"mensaje": "Ambulancia eliminada."}, 204

# Vista para gestionar los formularios de accidente


# Vista para gestionar los formularios de accidente

class VistaFormularioAccidente(Resource):
    def get(self):
        try:
            formularios = FormularioAccidente.query.all()
            return [formulario.to_dict() for formulario in formularios], 200
        except Exception as e:
            return {"mensaje": f"Error al obtener los formularios: {str(e)}"}, 500

    def post(self):
        try:
            nuevo_formulario = FormularioAccidente(
                nombre=request.json.get('nombre', ''),
                apellido=request.json.get('apellido', ''),
                numero_documento=request.json.get('numero_documento', None),
                genero=request.json.get('genero', ''),
                seguro_medico=request.json.get('seguro_medico', None),
                reporte_accidente=request.json.get('reporte_accidente', ''),
                fecha_reporte=request.json.get('fecha_reporte', None),
                ubicacion=request.json.get('ubicacion', ''),
                EPS=request.json.get('EPS', ''),  # Nombre correcto
                estado=request.json.get('estado', ''),
                ambulancia_id=request.json.get('ambulancia_id', None)
            )
            db.session.add(nuevo_formulario)
            db.session.commit()
            return nuevo_formulario.to_dict(), 201
        except Exception as e:
            return {"mensaje": f"Error al crear el formulario: {str(e)}"}, 500

    def put(self, id):
        formulario = FormularioAccidente.query.get(id)
        if not formulario:
            return {"mensaje": "Formulario no encontrado."}, 404

        try:
            formulario.nombre = request.json.get('nombre', formulario.nombre)
            formulario.apellido = request.json.get('apellido', formulario.apellido)
            formulario.numero_documento = request.json.get('numero_documento', formulario.numero_documento)
            formulario.genero = request.json.get('genero', formulario.genero)
            formulario.seguro_medico = request.json.get('seguro_medico', formulario.seguro_medico)
            formulario.reporte_accidente = request.json.get('reporte_accidente', formulario.reporte_accidente)
            formulario.fecha_reporte = request.json.get('fecha_reporte', formulario.fecha_reporte)
            formulario.ubicacion = request.json.get('ubicacion', formulario.ubicacion)
            formulario.EPS = request.json.get('EPS', formulario.EPS)
            formulario.estado = request.json.get('estado', formulario.estado)
            formulario.ambulancia_id = request.json.get('ambulancia_id', formulario.ambulancia_id)

            db.session.commit()
            return formulario.to_dict(), 200
        except Exception as e:
            return {"mensaje": f"Error al actualizar el formulario: {str(e)}"}, 500

    def delete(self, id):
        formulario = FormularioAccidente.query.get(id)
        if not formulario:
            return {"mensaje": "Formulario no encontrado."}, 404

        try:
            db.session.delete(formulario)
            db.session.commit()
            return {"mensaje": "Formulario eliminado."}, 204
        except Exception as e:
            return {"mensaje": f"Error al eliminar el formulario: {str(e)}"}, 500

class VistaReporteViajes(Resource):
    def get(self):
        # Obtener todos los reportes de viaje
        reportes = ReporteViajes.query.all()
        return reportes_viajes_schema.dump(reportes), 200

    def post(self):
        # Crear un nuevo reporte de viaje
        try:
            nuevo_reporte = ReporteViajes(
               
                tiempo=request.json['tiempo'],
         
                punto_i=request.json.get('punto_i'),
                punto_f=request.json.get('punto_f'),
                accidente_id=request.json.get('accidente_id')
            )

            # Guardar en la base de datos
            db.session.add(nuevo_reporte)
            db.session.commit()
            return reporte_viajes_schema.dump(nuevo_reporte), 201
        except KeyError as e:
            return {"mensaje": f"Falta el campo {str(e)}"}, 400

    def put(self, id):
        # Actualizar un reporte de viaje existente
        reporte = ReporteViajes.query.get(id)
        if not reporte:
            return {"mensaje": "Reporte no encontrado."}, 404

        # Actualizar los campos con los nuevos valores si existen
       
        reporte.tiempo = request.json.get('tiempo', reporte.tiempo)
      
        reporte.punto_i = request.json.get('punto_i', reporte.punto_i)
        reporte.punto_f = request.json.get('punto_f', reporte.punto_f)
        reporte.accidente_id = request.json.get('accidente_id', reporte.accidente_id)

        # Guardar los cambios en la base de datos
        db.session.commit()
        return reporte_viajes_schema.dump(reporte), 200

    def delete(self, id):
        # Eliminar un reporte de viaje
        reporte = ReporteViajes.query.get(id)
        if not reporte:
            return {"mensaje": "Reporte no encontrado."}, 404

        # Eliminar el reporte de la base de datos
        db.session.delete(reporte)
        db.session.commit()
        return {"mensaje": "Reporte eliminado."}, 204
    
    
    
    
    
# Vista para gestionar los hospitales
class VistaHospitales(Resource):
    def get(self):
        """Obtiene todos los hospitales."""
        hospitales = Hospitales.query.all()
        return hospitales_schema.dump(hospitales), 200

    def post(self):
        """Crea un nuevo hospital."""
        # Obtén los datos del cuerpo de la solicitud
        nuevo_hospital = Hospitales(
            nombre=request.json['nombre'],
            direccion=request.json['direccion'],
            capacidad_atencion=request.json['capacidad_atencion'],
            categoria=request.json['categoria']
        )
        
        db.session.add(nuevo_hospital)
        db.session.commit()
        return hospital_schema.dump(nuevo_hospital), 201

    def put(self, id):
        """Actualiza los datos de un hospital."""
        hospital = Hospitales.query.get(id)
        if not hospital:
            return {"mensaje": "Hospital no encontrado."}, 404
        
        hospital.nombre = request.json.get('nombre', hospital.nombre)
        hospital.direccion = request.json.get('direccion', hospital.direccion)
        hospital.capacidad_atencion = request.json.get('capacidad_atencion', hospital.capacidad_atencion)
        hospital.categoria = request.json.get('categoria', hospital.categoria)
        
        db.session.commit()
        return hospital_schema.dump(hospital), 200

    def delete(self, id):
        """Elimina un hospital."""
        hospital = Hospitales.query.get(id)
        if not hospital:
            return {"mensaje": "Hospital no encontrado."}, 404

        db.session.delete(hospital)
        db.session.commit()
        return {"mensaje": "Hospital eliminado."}, 204




class VistaAsignacionAmbulancia(Resource):
    def get(self):
        """Obtener todas las asignaciones de ambulancia."""
        try:
            # Asegúrate de cargar las relaciones correctamente
            asignaciones = AsignacionAmbulancia.query.options(joinedload(AsignacionAmbulancia.ambulancia)).all()
            asignaciones_dict = [asignacion_ambulancia_schema.dump(asignacion) for asignacion in asignaciones]
            return asignaciones_dict, 200
        except Exception as e:
            return {"mensaje": f"Error al obtener las asignaciones: {str(e)}"}, 500
        
    def post(self):
        """Crear una nueva asignación de ambulancia."""
        try:
            personal_id = request.json.get('personal_id')
            ambulancia_id = request.json.get('ambulancia_id')

            # Validar entrada
            if not personal_id or not ambulancia_id:
                return {"mensaje": "Se deben proporcionar 'personal_id' y 'ambulancia_id'."}, 400

            # Verificar que el personal existe
            personal = Personal.query.get(personal_id)
            if not personal:
                return {"mensaje": "El personal no existe."}, 404

            # Verificar que la ambulancia existe
            ambulancia = Ambulancia.query.get(ambulancia_id)
            if not ambulancia:
                return {"mensaje": "La ambulancia no existe."}, 404
            if personal.personal_rol == RolesEnum.SUPERADMIN:
                return {"mensaje": "No se puede asignar un superadministrador a una ambulancia."}, 400
            # Restricción: no asignar administradores
            if personal.personal_rol == RolesEnum.ADMINISTRADOR:
                return {"mensaje": "No se puede asignar un administrador a una ambulancia."}, 400

            # Restricción: verificar si el personal ya está asignado a una ambulancia
            asignacion_existente = AsignacionAmbulancia.query.filter_by(personal_id=personal_id).first()
            if asignacion_existente:
                return {"mensaje": "El personal ya está asignado a otra ambulancia."}, 400

            # Restricción: verificar duplicidad de roles en la misma ambulancia
            roles_asignados = [asignacion.persona.rol.nombre for asignacion in ambulancia.asignaciones]
            if personal.rol.nombre in roles_asignados:
                return {"mensaje": f"La ambulancia ya tiene asignado un {personal.rol.nombre}."}, 400

            # Crear nueva asignación
            nueva_asignacion = AsignacionAmbulancia(
                personal_id=personal_id,
                ambulancia_id=ambulancia_id
            )
            db.session.add(nueva_asignacion)
            db.session.commit()

            return asignacion_ambulancia_schema.dump(nueva_asignacion), 201

        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "Error de integridad en la base de datos."}, 400
        except Exception as e:
            return {"mensaje": f"Error inesperado: {str(e)}"}, 500

    def put(self, id):
        """Actualizar una asignación existente."""
        asignacion = AsignacionAmbulancia.query.get(id)
        if not asignacion:
            return {"mensaje": "Asignación no encontrada."}, 404

        try:
            personal_id = request.json.get('personal_id', asignacion.personal_id)
            ambulancia_id = request.json.get('ambulancia_id', asignacion.ambulancia_id)

            # Verificar que el personal existe
            personal = Personal.query.get(personal_id)
            if not personal:
                return {"mensaje": "El personal no existe."}, 404

            # Verificar que la ambulancia existe
            ambulancia = Ambulancia.query.get(ambulancia_id)
            if not ambulancia:
                return {"mensaje": "La ambulancia no existe."}, 404
            if personal.personal_rol == RolesEnum.SUPERADMIN:
                return {"mensaje": "No se puede asignar un superadministrador a una ambulancia."}, 400
            # Restricción: no asignar administradores
            if personal.personal_rol == RolesEnum.ADMINISTRADOR:
                return {"mensaje": "No se puede asignar un administrador a una ambulancia."}, 400

            # Restricción: verificar si el personal ya está asignado a otra ambulancia
            asignacion_existente = AsignacionAmbulancia.query.filter_by(personal_id=personal_id).first()
            if asignacion_existente and asignacion_existente.id != id:
                return {"mensaje": "El personal ya está asignado a otra ambulancia."}, 400

            # Restricción: verificar duplicidad de roles en la misma ambulancia
            roles_asignados = [
                asignacion.persona.rol.nombre
                for asignacion in ambulancia.asignaciones
                if asignacion.id != id
            ]
            if personal.rol.nombre in roles_asignados:
                return {"mensaje": f"La ambulancia ya tiene asignado un {personal.rol.nombre}."}, 400

            # Actualizar asignación
            asignacion.personal_id = personal_id
            asignacion.ambulancia_id = ambulancia_id
            db.session.commit()

            return asignacion_ambulancia_schema.dump(asignacion), 200

        except IntegrityError:
            db.session.rollback()
            return {"mensaje": "Error de integridad en la base de datos."}, 400
        except Exception as e:
            return {"mensaje": f"Error inesperado: {str(e)}"}, 500

    def delete(self, id):
        """Eliminar una asignación."""
        asignacion = AsignacionAmbulancia.query.get(id)
        if not asignacion:
            return {"mensaje": "Asignación no encontrada."}, 404

        try:
            db.session.delete(asignacion)
            db.session.commit()
            return {"mensaje": "Asignación eliminada."}, 204
        except Exception as e:
            return {"mensaje": f"Error al eliminar la asignación: {str(e)}"}, 500
