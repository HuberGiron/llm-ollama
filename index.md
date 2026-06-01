---
layout: default
title: Inicio
nav_order: 1
---

# CNC Plotter – Manual de Uso

Este sitio documenta una **CNC cartesiana de 3 ejes** basada en una arquitectura simple, modular y replicabl, se explica la estructura, mecanismos de transmisión, criterios de diseño, electrónica y flujo de puesta en marcha.

La documentación está organizada desde lo general hacia lo particular:

## Contenidos

1. [IA generativa y LLM](panorama-ia-generativa-llm.md)
2. [Recursos, costos y desempeño de LLM](panorama-ia-generativa-llm.md)


## En qué consiste este proyecto

Esta máquina usa una lógica típica de fabricación digital ligera:

- **Diseño mecánico modular** con perfilería de aluminio y piezas auxiliares.
- **Motores a pasos** para el accionamiento de los ejes.
- **Mecanismos de transmisión** que convierten rotación en movimiento lineal.
- **Controlador basado en Arduino UNO + CNC Shield + drivers A4988**.
- **Firmware GRBL 1.1** para interpretar comandos de movimiento.
- **OpenBuilds CONTROL** como sender para pruebas y ejecución de G-code.
- **Flujo CAD/CAM** para pasar de un diseño digital a trayectorias reales de máquina.


## Requisitos básicos

- Computadora con Windows, macOS o Linux.
- Conexión USB al Arduino.
- Fuente de alimentación para motores (12–24 V).
- Máquina armada o parcialmente armada para realizar pruebas.

## Sugerencia de lectura

Si es tu primera vez con una máquina CNC, conviene seguir este orden:

1. Arquitectura general.
2. Motores y mecanismos.
3. Diseño mecánico de esta CNC.
4. Hardware.
5. Software.
6. Calibración.
7. Primer G-code.
8. Flujo FabModules.