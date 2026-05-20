import datetime
import logging
from abc import ABC, abstractmethod

# Configuración del Sistema de Logs (Persistencia de eventos)
logging.basicConfig(
    filename='errores_sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# ==========================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================

class SoftwareFJError(Exception):
    """Clase base para excepciones del sistema FJ."""
    pass

class DatoInvalidoError(SoftwareFJError):
    """Se dispara cuando los datos de entrada no cumplen el formato."""
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    """Se dispara cuando un recurso ya está ocupado."""
    pass

class GestionFinancieraError(SoftwareFJError):
    """Se dispara por problemas de costos o pagos."""
    pass

# ==========================================
# ARQUITECTURA BASE (POO AVANZADO)
# ==========================================

class EntidadBase(ABC):
    """Clase abstracta para asegurar que cada entidad tenga un ID único."""
    
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad

    @abstractmethod
    def __str__(self):
        pass

# ==========================================
# ENTIDAD CLIENTE (ENCAPSULAMIENTO)
# ==========================================

class Cliente(EntidadBase):
    """Gestiona la información y validación de los clientes de Software FJ."""

    def __init__(self, id_cliente, nombre, email):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.email = email
        self._fecha_registro = datetime.date.today()

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor) < 3:
            raise DatoInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if "@" not in valor or "." not in valor:
            raise DatoInvalidoError(f"Email inválido detectado: {valor}")
        self._email = valor

    def __str__(self):
        return f"Cliente: {self._nombre} | ID: {self._id_entidad}"

# ==========================================
# JERARQUÍA DE SERVICIOS (POLIMORFISMO)
# ==========================================

class Servicio(ABC):
    """Define la interfaz para los servicios ofrecidos."""
    
    def __init__(self, nombre_servicio, tarifa_base):
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base

    @abstractmethod
    def calcular_costo(self, cantidad):
        """Calcula el costo total según el tipo de servicio."""
        pass

    def __str__(self):
        return f"Servicio: {self.nombre_servicio}"

class ReservaSala(Servicio):
    def calcular_costo(self, horas):
        # Las salas tienen un recargo por mantenimiento fijo
        return (self.tarifa_base * horas) + 15.0

class AlquilerEquipo(Servicio):
    def calcular_costo(self, dias):
        # Descuento si es más de una semana
        costo = self.tarifa_base * dias
        return costo * 0.9 if dias > 7 else costo

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, sesiones):
        # Tarifa plana por sesión de consultoría
        return self.tarifa_base * sesiones

# ==========================================
# GESTIÓN DE RESERVAS
# ==========================================

class Reserva:
    """Clase mediadora que integra Clientes y Servicios."""
    
    ESTADOS = ['Pendiente', 'Confirmada', 'Cancelada']

    def __init__(self, cliente, servicio, magnitud):
        self.cliente = cliente
        self.servicio = servicio
        self.magnitud = magnitud  # Horas, días o sesiones
        self._estado = 'Pendiente'
        self._costo_total = self.servicio.calcular_costo(magnitud)

    def confirmar(self):
        if self._estado == 'Cancelada':
            raise ServicioNoDisponibleError("No se puede confirmar una reserva previamente cancelada.")
        self._estado = 'Confirmada'
        logging.info(f"Reserva exitosa: {self.cliente.nombre} - {self.servicio.nombre_servicio}")

    def cancelar(self):
        self._estado = 'Cancelada'
        logging.warning(f"Reserva cancelada para: {self.cliente.nombre}")

    def __str__(self):
        return f"Reserva [{self._estado}] | {self.cliente.nombre} | {self.servicio.nombre_servicio} | Total: ${self._costo_total:.2f}"

# ==========================================
# SIMULACIÓN (MAIN)
# ==========================================

def ejecutar_prueba(id_test, descripcion, accion):
    """Helper para ejecutar pruebas con manejo de errores limpio."""
    print(f"\n--- Prueba {id_test}: {descripcion} ---")
    try:
        resultado = accion()
        if resultado: print(f"[ÉXITO] {resultado}")
    except (DatoInvalidoError, ServicioNoDisponibleError, GestionFinancieraError) as e:
        mensaje_error = f"Error de Negocio: {e}"
        print(f"[FALLO ESPERADO] {mensaje_error}")
        logging.error(mensaje_error)
    except Exception as e:
        mensaje_critico = f"Fallo Crítico Inesperado: {e}"
        print(f"[CRÍTICO] {mensaje_critico}")
        logging.critical(mensaje_critico, exc_info=True)
    finally:
        print("Finalizando operación...")

def main():
    """Simulación principal del flujo de trabajo de Software FJ."""
    
    # 1. Registro de Clientes (Casos de éxito y fallo)
    clientes_validos = []
    
    ejecutar_prueba(1, "Crear cliente válido", 
                   lambda: (clientes_validos.append(Cliente(101, "Juan Perez", "juan@fj.com")), "Juan creado")[1])
    
    ejecutar_prueba(2, "Crear cliente con email corrupto", 
                   lambda: Cliente(102, "Maria Garcia", "maria_at_fj.com"))
    
    ejecutar_prueba(3, "Crear cliente con nombre corto", 
                   lambda: Cliente(103, "Jo", "jo@fj.com"))

    # 2. Definición de Catálogo de Servicios
    sala_reunion = ReservaSala("Sala Proyectos", 50.0)
    laptop_dev = AlquilerEquipo("MacBook Pro", 30.0)
    consultoria = AsesoriaEspecializada("Arquitectura Software", 120.0)

    # 3. Operaciones de Reserva
    def test_reserva_exitosa():
        res = Reserva(clientes_validos[0], sala_reunion, 4)
        res.confirmar()
        return res

    ejecutar_prueba(4, "Reserva de Sala (4 horas)", test_reserva_exitosa)

    def test_alquiler_largo():
        res = Reserva(clientes_validos[0], laptop_dev, 10) # Aplica descuento
        return res

    ejecutar_prueba(5, "Alquiler de Equipo > 7 días", test_alquiler_largo)

    # 4. Manejo de estados y lógica de negocio
    def test_cancelacion_reconfirmada():
        res = Reserva(clientes_validos[0], consultoria, 2)
        res.cancelar()
        res.confirmar() # Debería fallar
        return res

    ejecutar_prueba(6, "Intentar confirmar reserva cancelada", test_cancelacion_reconfirmada)

    # 5. Más casos de borde
    ejecutar_prueba(7, "Asesoría puntual", 
                   lambda: Reserva(clientes_validos[0], consultoria, 1))

    # Simulando un error de sistema por datos nulos (Encadenamiento)
    def test_error_encadenado():
        try:
            c = Cliente(999, "Error Humano", "error@test.com")
            # Forzamos un error de lógica
            raise ValueError("Valor de sistema corrupto")
        except ValueError as e:
            raise GestionFinancieraError("No se pudo procesar el pago por error de sistema") from e

    ejecutar_prueba(8, "Simulación de Error Encadenado", test_error_encadenado)

    ejecutar_prueba(9, "Reserva con cliente existente", 
                   lambda: Reserva(clientes_validos[0], laptop_dev, 2))

    ejecutar_prueba(10, "Finalización de jornada", lambda: "Sistema en espera de nuevas solicitudes.")

    print("\n" + "="*50)
    print("PROCESO FINALIZADO: Revise 'errores_sistema.log' para el historial completo.")
    print("="*50)

if __name__ == "__main__":
    main()