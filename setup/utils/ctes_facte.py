# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

log = logging.getLogger(__name__)

APP_FMT_FECHA_SRI = "%d%m%Y"
AMBIENTE_PRUEBAS = "1"
AMBIENTE_PRODUCCION = "2"

COD_DOC_FACTURA = "01"

SI = "SI"

TIPO_COMPRADOR_RUC = "04"
TIPO_COMPRADOR_CEDULA = "05"
TIPO_COMPRADOR_PASAPORTE = "06"
TIPO_COMPRADOR_CONSFINAL = "07"
TIPO_COMPRADOR_IDENT_EXT = "08"

LENGTH_CEDULA_ECU = 10
LENGTH_RUC_ECU = 13

CODIGO_IMPUESTO_IVA = "2"
CODIGO_IVA_CERO = "0"
CODIGO_IVA_12 = "2"
CODIGO_IVA_14 = "3"
CODIGO_NO_OBJ_IMPUESTO = "6"
CODIGO_EXCENTO_IVA = "7"

MONEDA = "DOLAR"

PAGO_SIN_UTILIZACION_SIS_FINANCIERO = "01"
PAGO_COMPENSACION_DEUDAS = "15"
PAGO_TARJETA_CREDITO = "19"
PAGO_TARJETA_PREPAGO = "18"
PAGO_OTROS_SIN_UTILIZACION = "20"
PAGO_ENDOSO_TITULOS = "21"

URI_RIDE_PDF = "http://localhost:8080/imprentas/RideServlet"
URI_RIDE_XML = "http://localhost:8080/imprentas/XmlCompeServlet"
