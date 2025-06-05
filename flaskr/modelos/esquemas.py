from marshmallow import fields, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .modelo import RolesEnum, CategoriaAmbulanciaEnum, GeneroEnum, EstadoAccidenteEnum
from .modelo import AsignacionAmbulancia, Roles, Ambulancia, Personal, FormularioAccidente, ReporteViajes, Hospitales


class RolesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Roles
        load_instance = True


class AmbulanciaSchema(SQLAlchemyAutoSchema):
    categoria_ambulancia = fields.Str(attribute="categoria_ambulancia.value")  # Serializa el valor del Enum como un string
    hospital_id = fields.Int(attribute="hospital_id", dump_only=True)  # Incluir hospital_id

    @validates('categoria_ambulancia')
    def validate_categoria_ambulancia(self, value):
        if value not in [cat.value for cat in CategoriaAmbulanciaEnum]:
            raise ValidationError(f"Categoría no válida. Debe ser uno de: {', '.join([cat.value for cat in CategoriaAmbulanciaEnum])}")

    class Meta:
        model = Ambulancia
        include_relationships = True
        load_instance = True


class PersonalSchema(SQLAlchemyAutoSchema):
    personal_rol = fields.String(attribute="rol.nombre", dump_only=True)  # Cambia el ID por el nombre del rol

    @validates('personal_rol')
    def validate_personal_rol(self, value):
        if value not in [role.value for role in RolesEnum]:
            raise ValidationError(f"El valor del rol no es válido. Debe ser uno de: {', '.join([role.value for role in RolesEnum])}")

    class Meta:
        model = Personal
        load_instance = True
        include_relationships = True


class FormularioAccidenteSchema(SQLAlchemyAutoSchema):
    genero = fields.Str(attribute="genero.value")  # Serializa el valor de GeneroEnum como un string
    estado = fields.Str(attribute="estado.value")  # Serializa el valor de EstadoAccidenteEnum como un string

    class Meta:
        model = FormularioAccidente
        include_relationships = True
        load_instance = True


class ReporteViajesSchema(SQLAlchemyAutoSchema):
    accidente = fields.Nested('FormularioAccidenteSchema')  # Relación con FormularioAccidente
    ambulancia_asignada = fields.Int(data_key="ambulancia_id")  # Muestra como 'ambulancia_id' en la respuesta
    accidente_id = fields.Int()  # Mostrar 'accidente_id'

    class Meta:
        model = ReporteViajes
        include_relationships = True
        load_instance = True


class HospitalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Hospitales
        include_relationships = True
        load_instance = True


class AsignacionAmbulanciaSchema(SQLAlchemyAutoSchema):
    persona = fields.Nested('PersonalSchema')  # Relación con Personal
    ambulancia = fields.Nested('AmbulanciaSchema')  # Relación con Ambulancia
    personal_id = fields.Int(attribute="personal_id", dump_only=True)  # Agregar personal_id
    ambulancia_id = fields.Int(attribute="ambulancia_id", dump_only=True)  # Asegurarse de incluir 'ambulancia_id'
    rol_persona = fields.String(attribute="persona.rol.nombre", dump_only=True)  # Mostrar el rol de la persona sin permitir modificarlo

    @validates('rol_persona')
    def validate_rol(self, value):
        raise ValidationError("El rol no puede ser modificado porque está vinculado a una asignación existente.")

    class Meta:
        model = AsignacionAmbulancia
        include_relationships = True
        load_instance = True