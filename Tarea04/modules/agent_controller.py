import time
import config


class AgentController:
    
#    Orquesta las transiciones de estado de Robot2D en respuesta a los eventos de Pose y gestos.
#    Flujo por evento: Deteccion -> Interpretacion -> Saludo/Despedida/Ejecucion -> Exito/Error -> Espera

    TIEMPO_DETECCION      = 0.6
    TIEMPO_INTERPRETACION = 0.9
    TIEMPO_REACCION       = 1.2
    TIEMPO_EJECUCION      = 0.7
    TIEMPO_RESULTADO      = 3.0

    _RESPUESTAS = {
        config.EVENT_PERSONA_APARECE:    "Saludar",
        config.EVENT_MANO_LEVANTADA:     "Responder saludo",
        config.EVENT_PULGAR_ARRIBA:      "Confirmar",
        config.EVENT_PULGAR_ABAJO:       "Cambiar respuesta",
        config.EVENT_SENALAR_IZQUIERDA:  "Mostrar opcion izquierda",
        config.EVENT_SENALAR_DERECHA:    "Mostrar opcion derecha",
        config.EVENT_BRAZOS_CRUZADOS:    "Reiniciar seleccion",
        config.EVENT_PERSONA_SE_ACERCA:  "Activar interaccion",
        config.EVENT_PERSONA_DESAPARECE: "Despedirse",
    }

    def __init__(self, robot):
        self.robot   = robot
        self.mensaje = "Esperando interaccion"

        self.opcion_seleccionada = None
        self.interaccion_activa  = False
        self.aprobado            = None

        self._ultimo_evento      = config.EVENT_NINGUNO
        self._evento_activo      = config.EVENT_NINGUNO
        self._etapa              = None
        self._inicio_etapa       = time.perf_counter()
        self._presencia_atendida = False

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def forzar_error(self, detalle="Error de prueba"):
        """Fuerza el estado Error para capturar evidencia del sprite."""
        self.mensaje = detalle
        self.robot.finalizar_accion(False, detalle)
        self._etapa        = self.robot.estado
        self._inicio_etapa = time.perf_counter()
        self._ultimo_evento = config.EVENT_NINGUNO
        print(f"[AURA] {self.robot.estado} | {self.mensaje}", flush=True)

    def update(self, evento, presente=None):
        """Llamar una vez por cuadro con el evento combinado Pose + gestos.
        presente: pose_detector.person_present; None conserva comportamiento anterior.
        """
        ahora  = time.perf_counter()
        evento = evento or config.EVENT_NINGUNO

        # Secuencia activa: avanzarla sin interrumpir aunque el sensor cambie.
        if self._etapa is not None:
            self._avanzar_etapa(ahora)
            return

        # Sincronizar presencia: si el estado real difiere del atendido, forzar evento.
        # Esto garantiza que DESAPARECE se despacha aunque ocurriera durante la secuencia.
        if presente is not None and presente != self._presencia_atendida:
            evento = (config.EVENT_PERSONA_APARECE
                      if presente else config.EVENT_PERSONA_DESAPARECE)
            self._ultimo_evento = config.EVENT_NINGUNO  # fuerza el disparo

        # Filtrar transiciones redundantes de presencia
        if evento == config.EVENT_PERSONA_APARECE and self._presencia_atendida:
            evento = config.EVENT_NINGUNO
        if evento == config.EVENT_PERSONA_DESAPARECE and not self._presencia_atendida:
            evento = config.EVENT_NINGUNO

        # Actualizar estado de presencia al despachar un evento de presencia
        if evento in (config.EVENT_PERSONA_APARECE, config.EVENT_PERSONA_DESAPARECE):
            self._presencia_atendida = (evento == config.EVENT_PERSONA_APARECE)

        if evento != self._ultimo_evento:
            self._ultimo_evento = evento
            if evento != config.EVENT_NINGUNO:
                self._iniciar_evento(evento, ahora)

    # ------------------------------------------------------------------
    # Transiciones internas
    # ------------------------------------------------------------------

    def _iniciar_evento(self, evento, ahora):
        self._evento_activo = evento
        self.robot.actualizar(evento, estado_agente=self.robot.DETECCION)
        self.robot.detalle_resultado = ""
        self.robot.respuesta = self._RESPUESTAS.get(evento, "")

        if evento == config.EVENT_BRAZOS_CRUZADOS:
            self.robot.interpretacion = "Comando definido: reiniciar seleccion"

        self.mensaje = "Evento detectado"
        self._cambiar_etapa(self.robot.DETECCION, ahora)

    def _cambiar_etapa(self, etapa, ahora):
        self._etapa        = etapa
        self._inicio_etapa = ahora

        if etapa == self.robot.DETECCION:
            self.robot.iniciar_deteccion()
        elif etapa == self.robot.INTERPRETACION:
            self.robot.iniciar_interpretacion()
        elif etapa == self.robot.EJECUCION:
            self.robot.iniciar_ejecucion()
        else:
            self.robot.cambiar_estado(etapa)

        print(f"[AURA] {self._evento_activo} | {self.robot.estado}", flush=True)

    def _avanzar_etapa(self, ahora):
        if self._etapa is None:
            return

        t = ahora - self._inicio_etapa

        if self._etapa == self.robot.DETECCION:
            if t >= self.TIEMPO_DETECCION:
                self.mensaje = "Interpretando evento"
                self._cambiar_etapa(self.robot.INTERPRETACION, ahora)

        elif self._etapa == self.robot.INTERPRETACION:
            if t >= self.TIEMPO_INTERPRETACION:
                if self._evento_activo in (
                    config.EVENT_PERSONA_APARECE,
                    config.EVENT_MANO_LEVANTADA,
                ):
                    siguiente = self.robot.SALUDO
                elif self._evento_activo == config.EVENT_PERSONA_DESAPARECE:
                    siguiente = self.robot.DESPEDIDA
                else:
                    siguiente = self.robot.EJECUCION
                self._cambiar_etapa(siguiente, ahora)

        elif self._etapa in (self.robot.SALUDO, self.robot.DESPEDIDA):
            if t >= self.TIEMPO_REACCION:
                self._cambiar_etapa(self.robot.EJECUCION, ahora)

        elif self._etapa == self.robot.EJECUCION:
            if t >= self.TIEMPO_EJECUCION:
                try:
                    detalle = self._ejecutar_respuesta()
                except Exception as error:
                    self.mensaje = f"Error: {error}"
                    self.robot.finalizar_accion(False, self.mensaje)
                else:
                    self.robot.finalizar_accion(True, detalle)

                self._etapa        = self.robot.estado
                self._inicio_etapa = ahora
                print(f"[AURA] {self.robot.estado} | {self.mensaje}", flush=True)

        elif self._etapa in (self.robot.EXITO, self.robot.ERROR):
            if t >= self.TIEMPO_RESULTADO:
                self.robot.actualizar(
                    config.EVENT_NINGUNO,
                    estado_agente=self.robot.ESPERA
                )
                self.robot.volver_a_espera()
                self._etapa  = None
                # _ultimo_evento se conserva: si el mismo gesto/evento sigue
                # activo en el sensor, no se re-dispara hasta que el usuario
                # lo suelte (vuelva a NINGUNO) y lo repita.
                self.mensaje = "Esperando un nuevo evento"

    def _ejecutar_respuesta(self):
        ev = self._evento_activo

        if ev == config.EVENT_PERSONA_APARECE:
            self.interaccion_activa = True
            self.mensaje = "Hola, bienvenido a AURA"
        elif ev == config.EVENT_MANO_LEVANTADA:
            self.mensaje = "Hola, he recibido tu saludo"
        elif ev == config.EVENT_PULGAR_ARRIBA:
            self.aprobado = True
            self.mensaje  = "Respuesta confirmada"
        elif ev == config.EVENT_PULGAR_ABAJO:
            self.aprobado            = False
            self.opcion_seleccionada = None
            self.mensaje = "Respuesta rechazada; selecciona otra opcion"
        elif ev == config.EVENT_SENALAR_IZQUIERDA:
            self.opcion_seleccionada = "Izquierda"
            self.aprobado = None
            self.mensaje  = "Opcion izquierda seleccionada"
        elif ev == config.EVENT_SENALAR_DERECHA:
            self.opcion_seleccionada = "Derecha"
            self.aprobado = None
            self.mensaje  = "Opcion derecha seleccionada"
        elif ev == config.EVENT_BRAZOS_CRUZADOS:
            self.opcion_seleccionada = None
            self.aprobado = None
            self.mensaje  = "Seleccion reiniciada"
        elif ev == config.EVENT_PERSONA_SE_ACERCA:
            self.interaccion_activa = True
            self.mensaje = "Interaccion activada"
        elif ev == config.EVENT_PERSONA_DESAPARECE:
            self.interaccion_activa = False
            self.mensaje = "Hasta pronto"
        else:
            raise ValueError(f"Sin respuesta definida para: {ev}")

        return self.mensaje
