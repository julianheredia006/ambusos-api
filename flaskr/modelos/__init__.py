from .modelo import db, AsignacionAmbulancia, Roles, Ambulancia, Personal, FormularioAccidente, ReporteViajes, Hospitales
from .esquemas import AsignacionAmbulanciaSchema, RolesSchema, AmbulanciaSchema, PersonalSchema, FormularioAccidenteSchema, ReporteViajesSchema, HospitalSchema
from .modelo import RolesEnum, CategoriaAmbulanciaEnum, GeneroEnum, EstadoAccidenteEnum

__all__ = [
    "db",
    "Roles",
    "Ambulancia",
    "Personal",
    "FormularioAccidente",
    "ReporteViajes",
    "RolesSchema",
    "AmbulanciaSchema",
    "PersonalSchema",
    "FormularioAccidenteSchema",
    "ReporteViajesSchema",
    "AsignacionAmbulancia",          # Se agrega la nueva tabla
    "AsignacionAmbulanciaSchema",    # Se agrega la nueva serialización
    "Hospitales",                    # Se agrega el nuevo modelo Hospitales
    "HospitalSchema",                # Se agrega el nuevo esquema HospitalSchema
]
