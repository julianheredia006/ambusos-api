from marshmallow import fields, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .modelo import (
    RolesEnum,
    CategoriaAmbulanciaEnum,
    GeneroEnum,
    EstadoAccidenteEnum,
    AsignacionAmbulancia,
    Roles,
    Ambulancia,
    Personal,
    FormularioAccidente,
    ReporteViajes,
    Hospitales
)

class RolesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Roles
        load_instance = True


class AmbulanciaSchema(SQLAlchemyAutoSchema):
    categoria_ambulancia = fields.String()

    @validates('categoria_ambulancia')
    def validate_categoria_ambulancia(self, value):
        if value not in [cat.value for cat in CategoriaAmbulanciaEnum]:
            raise ValidationError(f"Categoría no válida. Debe ser una de: {', '.join(cat.value for cat in CategoriaAmbulanciaEnum)}")

    class Meta:
        model = Ambulancia
        include_relationships = True
        load_instance = True


class PersonalSchema(SQLAlchemyAutoSchema):
    rol = fields.String(attribute="rol.nombre", dump_only=True)

    class Meta:
        model = Personal
        load_instance = True
        include_relationships = True


class FormularioAccidenteSchema(SQLAlchemyAutoSchema):
    genero = fields.String()
    estado = fields.String()

    @validates('genero')
    def validate_genero(self, value):
        if value not in [g.value for g in GeneroEnum]:
            raise ValidationError(f"Género no válido. Debe ser uno de: {', '.join(g.value for g in GeneroEnum)}")

    @validates('estado')
    def validate_estado(self, value):
        if value not in [e.value for e in EstadoAccidenteEnum]:
            raise ValidationError(f"Estado no válido. Debe ser uno de: {', '.join(e.value for e in EstadoAccidenteEnum)}")

    class Meta:
        model = FormularioAccidente
        include_relationships = True
        load_instance = True


class ReporteViajesSchema(SQLAlchemyAutoSchema):
    accidente = fields.Nested(FormularioAccidenteSchema)
    accidente_id = fields.Int()

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
    persona = fields.Nested(PersonalSchema)
    ambulancia = fields.Nested(AmbulanciaSchema)
    personal_id = fields.Int()
    ambulancia_id = fields.Int()
    rol_persona = fields.String(attribute="persona.rol.nombre", dump_only=True)

    class Meta:
        model = AsignacionAmbulancia
        include_relationships = True
        load_instance = True
