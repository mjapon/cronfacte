# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import itertools
import logging
import xml.etree.ElementTree as et

from setup.models.conf import BaseDao
from setup.utils import fechas, ctes, ctes_facte, cadenas, numeros

log = logging.getLogger(__name__)


class GeneraFacturaCompEle(BaseDao):

    def generar_nota_credito(self, ambiente_value, datos_notacred, datos_alm_matriz,
                             totales, detalles_db, datos_factura_anul,
                             tipo_emision_value=1):
        root = et.Element('notaCredito')
        root.set("id", "comprobante")
        root.set("version", "1.0.0")

        info_tributaria = et.SubElement(root, "infoTributaria")
        ambiente = et.SubElement(info_tributaria, "ambiente")
        ambiente.text = str(ambiente_value)

        tipo_emision = et.SubElement(info_tributaria, "tipoEmision")
        tipo_emision.text = str(tipo_emision_value)

        razon_social = et.SubElement(info_tributaria, "razonSocial")
        razon_social.text = cadenas.strip(datos_notacred['alm_razsoc'])

        nombre_comercial = et.SubElement(info_tributaria, "nombreComercial")
        nombre_comercial.text = cadenas.strip(datos_notacred['alm_nomcomercial'])

        ruc = et.SubElement(info_tributaria, "ruc")
        ruc.text = cadenas.strip((datos_notacred['alm_ruc']))

        clave_acceso_value = self.get_clave_acceso(datos_factura=datos_notacred, tipo_ambiente=str(ambiente_value),
                                                   tipo_comprobante=ctes_facte.COD_DOC_NOTA_CREDITO)
        clave_acceso = et.SubElement(info_tributaria, "claveAcceso")
        clave_acceso.text = clave_acceso_value

        cod_doc = et.SubElement(info_tributaria, "codDoc")
        cod_doc.text = ctes_facte.COD_DOC_NOTA_CREDITO

        estab = et.SubElement(info_tributaria, "estab")
        estab.text = str(datos_notacred['alm_numest'])

        pto_emi = et.SubElement(info_tributaria, "ptoEmi")
        pto_emi.text = str(datos_notacred['tdv_numero'])

        secuencial = et.SubElement(info_tributaria, "secuencial")
        trn_compro = datos_notacred['trn_compro']

        secuencial_value = trn_compro[6:]
        secuencial.text = secuencial_value

        alm_matriz_value = datos_alm_matriz['alm_direcc']

        dir_matriz = et.SubElement(info_tributaria, "dirMatriz")
        dir_matriz.text = alm_matriz_value

        info_nota_credito = et.SubElement(root, "infoNotaCredito")

        fecha_emision = et.SubElement(info_nota_credito, "fechaEmision")
        fecha_emision.text = datos_notacred['trn_fecreg']

        dir_establecimiento = et.SubElement(info_nota_credito, "dirEstablecimiento")
        dir_establecimiento.text = datos_notacred['alm_direcc']

        tipoidentcomprador_value = self.get_tipo_ident_comprador(per_codigo=datos_notacred['per_codigo'],
                                                                 per_ciruc=datos_notacred['per_ciruc'])
        tipo_ident_comprador = et.SubElement(info_nota_credito, "tipoIdentificacionComprador")
        tipo_ident_comprador.text = str(tipoidentcomprador_value)

        razon_social_comprador = et.SubElement(info_nota_credito, "razonSocialComprador")
        razon_social_comprador.text = cadenas.clean_for_rentas(cadenas.strip_upper(datos_notacred['per_nomapel']))[
                                      0:300]

        identificacion_comprador = et.SubElement(info_nota_credito, "identificacionComprador")
        identificacion_comprador.text = cadenas.strip(datos_notacred['per_ciruc'])[0:20]

        cnt_codigo = datos_alm_matriz['cnt_codigo']
        if cnt_codigo > 0:
            contribuyente_especial = et.SubElement(info_nota_credito, "contribuyenteEspecial")
            contribuyente_especial.text = str(cnt_codigo)

        alm_contab = datos_alm_matriz['alm_contab']
        if alm_contab:
            obligado_contab = et.SubElement(info_nota_credito, "obligadoContabilidad")
            obligado_contab.text = ctes_facte.SI

        cod_doc_modificado = et.SubElement(info_nota_credito, "codDocModificado")
        cod_doc_modificado.text = ctes_facte.COD_DOC_FACTURA

        numero_factura_modifica = datos_factura_anul['trn_compro']
        num_doc_modificado = et.SubElement(info_nota_credito, "numDocModificado")
        num_doc_modificado.text = "{0}-{1}-{2}".format(numero_factura_modifica[:3],
                                                       numero_factura_modifica[3:6],numero_factura_modifica[6:])

        fecha_emision_doc_sustento = et.SubElement(info_nota_credito, "fechaEmisionDocSustento")
        fecha_emision_doc_sustento.text = datos_factura_anul['trn_fecreg']

        total_sin_impuestos = et.SubElement(info_nota_credito, "totalSinImpuestos")
        total_sin_impuestos.text = str(numeros.roundm2(totales['total_sin_impuesto']))

        valor_modificacion = et.SubElement(info_nota_credito, "valorModificacion")
        valor_modificacion.text = str(numeros.roundm2(totales['total']))

        moneda = et.SubElement(info_nota_credito, "moneda")
        moneda.text = ctes_facte.MONEDA

        total_con_impuestos = et.SubElement(info_nota_credito, "totalConImpuestos")
        total_impuesto = et.SubElement(total_con_impuestos, "totalImpuesto")

        codigo_impuesto_item = et.SubElement(total_impuesto, "codigo")
        codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

        codigo_porcentaje = et.SubElement(total_impuesto, "codigoPorcentaje")
        codigo_porcentaje.text = ctes_facte.CODIGO_IVA_15

        base_imponible = et.SubElement(total_impuesto, "baseImponible")
        base_imponible.text = str(numeros.roundm2(totales['base_imp_iva_15']))

        valor_impuesto = et.SubElement(total_impuesto, "valor")
        valor_impuesto.text = str(numeros.roundm2(totales['impuesto_iva_15']))

        if totales['base_imp_iva_5'] > 0:
            total_impuesto_5 = et.SubElement(total_con_impuestos, "totalImpuesto")

            codigo_impuesto_item = et.SubElement(total_impuesto_5, "codigo")
            codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

            codigo_porcentaje = et.SubElement(total_impuesto_5, "codigoPorcentaje")
            codigo_porcentaje.text = ctes_facte.CODIGO_IVA_5

            base_imponible = et.SubElement(total_impuesto_5, "baseImponible")
            base_imponible.text = str(numeros.roundm2(totales['base_imp_iva_5']))

            valor_impuesto = et.SubElement(total_impuesto_5, "valor")
            valor_impuesto.text = str(numeros.roundm2(totales['impuesto_iva_5']))

        motivo = et.SubElement(info_nota_credito, "motivo")
        motivo.text = ctes_facte.MOTIVO_DEVOLUCION

        detalles = et.SubElement(root, "detalles")

        for detalle_db in detalles_db:
            detalle_item = et.SubElement(detalles, "detalle")

            codigo_interno_item = et.SubElement(detalle_item, "codigoInterno")
            codigo_interno_item.text = cadenas.clean_for_rentas(cadenas.strip(detalle_db['ic_code']))[0:25]

            descripcion_item = et.SubElement(detalle_item, "descripcion")
            descripcion_item.text = cadenas.clean_for_rentas(cadenas.strip_upper(detalle_db['ic_nombre']))[0:300]

            cantidad_item = et.SubElement(detalle_item, "cantidad")
            cantidad_item.text = str(numeros.roundm2(detalle_db['dt_cant']))

            precio_unitario_item = et.SubElement(detalle_item, "precioUnitario")
            precio_unitario_item.text = str(numeros.roundm2(detalle_db['dt_precio']))

            descuento_fila_val = (detalle_db['dt_decto'] * detalle_db['dt_cant']) + detalle_db['dt_dectogen']
            descuento_fila_round = numeros.roundm2(descuento_fila_val)

            descuento_item = et.SubElement(detalle_item, "descuento")
            descuento_item.text = str(descuento_fila_round)

            precio_total_sin_impuesto_val = detalle_db['subtotal'] - descuento_fila_val

            precio_total_sin_impuesto_item = et.SubElement(detalle_item, "precioTotalSinImpuesto")
            precio_total_sin_impuesto_item.text = str(numeros.roundm2(precio_total_sin_impuesto_val))

            impuestos = et.SubElement(detalle_item, "impuestos")
            impuesto_item = et.SubElement(impuestos, "impuesto")

            codigo_impuesto_item = et.SubElement(impuesto_item, "codigo")
            codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

            dt_cant = detalle_db['dt_cant']
            dai_impg = detalle_db['dai_impg']
            dai_impg_mult = numeros.roundm2(dai_impg * 100)
            dt_decto = detalle_db['dt_decto']
            dt_decto_cant = dt_decto * dt_cant
            if detalle_db['dt_valdto'] >= 0.0:
                dt_decto_cant = dt_decto
            dt_dectogen = detalle_db['dt_dectogen']
            dt_precio = detalle_db['dt_precio']
            subtforiva = (dt_cant * dt_precio) - (dt_decto_cant + dt_dectogen)

            # subt = (detalle_db['dt_cant'] * detalle_db['dt_precio']) - detalle_db['dt_valdto']

            if dai_impg > 0:
                ivaval = numeros.get_valor_iva(subtforiva, dai_impg)
                codigo_porcentaje_impuesto_item = et.SubElement(impuesto_item, "codigoPorcentaje")
                if dai_impg == 0.05:
                    codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_5
                else:
                    codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_15
                tarifa_impuesto_item = et.SubElement(impuesto_item, "tarifa")
                tarifa_impuesto_item.text = str(dai_impg_mult)
                base_imponible_impuesto_item = et.SubElement(impuesto_item, "baseImponible")
                base_imponible_impuesto_item.text = str(numeros.roundm2(subtforiva))
                valor_impuesto_item = et.SubElement(impuesto_item, "valor")
                valor_impuesto_item.text = str(numeros.roundm2(ivaval))
            else:
                codigo_porcentaje_impuesto_item = et.SubElement(impuesto_item, "codigoPorcentaje")
                codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_CERO
                tarifa_impuesto_item = et.SubElement(impuesto_item, "tarifa")
                tarifa_impuesto_item.text = "0.00"
                base_imponible_impuesto_item = et.SubElement(impuesto_item, "baseImponible")
                base_imponible_impuesto_item.text = str(numeros.roundm2(subtforiva))
                valor_impuesto_item = et.SubElement(impuesto_item, "valor")
                valor_impuesto_item.text = "0.00"

        xml_str = et.tostring(root, encoding='utf8').decode('utf8')

        return {
            'clave': clave_acceso_value,
            'xml': xml_str
        }

    def get_clave_acceso(self, datos_factura, tipo_ambiente, tipo_comprobante=ctes_facte.COD_DOC_FACTURA):
        trn_fecreg = datos_factura['trn_fecreg']

        fechafact = fechas.format_cadena(trn_fecreg, ctes.APP_FMT_FECHA, ctes_facte.APP_FMT_FECHA_SRI)
        num_ruc = datos_factura['alm_ruc']

        trn_compro = datos_factura['trn_compro']
        serie_secuencial = trn_compro

        sec_id = datos_factura['sec_codigo']

        codigo_numerico = "0000000{0}".format(sec_id)  # potestad del contribuyente

        tipo_emision = "1"

        pre_clave_acceso = "{0}{1}{2}{3}{4}{5}{6}".format(fechafact, tipo_comprobante, num_ruc, tipo_ambiente,
                                                          serie_secuencial, codigo_numerico, tipo_emision)

        digito = self.get_digito_verificador(pre_clave_acceso)

        clave_acceso = '{0}{1}'.format(pre_clave_acceso, digito)

        return clave_acceso

    def get_digito_verificador(self, clave_acceso):

        factores = itertools.cycle((2, 3, 4, 5, 6, 7))
        suma = 0
        for digito, factor in zip(reversed(clave_acceso), factores):
            suma += int(digito) * factor
        control = 11 - suma % 11
        if control == 10:
            return 1
        elif control == 11:
            return 0
        else:
            return control

    def get_tipo_ident_comprador(self, per_codigo, per_ciruc):
        tipo_comprador = ctes_facte.TIPO_COMPRADOR_CONSFINAL
        per_ciruc = cadenas.strip(per_ciruc)
        if per_codigo == -1:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_CONSFINAL
        elif len(per_ciruc) == ctes_facte.LENGTH_CEDULA_ECU:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_CEDULA
        elif len(per_ciruc) == ctes_facte.LENGTH_RUC_ECU:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_RUC
        else:
            tipo_comprador = ctes_facte.TIPO_COMPRADOR_PASAPORTE

        return tipo_comprador

    def get_forma_pago(self, pagos_db):
        codigo_forma_pago = ctes_facte.PAGO_SIN_UTILIZACION_SIS_FINANCIERO
        if pagos_db is not None and len(pagos_db) == 1:
            type_pay = pagos_db[0].get('ic_clasecc')
            if type_pay is not None and type_pay != 'E':
                codigo_forma_pago = ctes_facte.PAGO_OTROS_CON_UTILIZACION_SIS_FINANCIERO
        return codigo_forma_pago

    def generar_factura(self, ambiente_value, datos_factura, datos_alm_matriz,
                        totales, detalles_db, pagos_db=None,
                        tipo_emision_value=1):

        root = et.Element('factura')
        root.set("id", "comprobante")
        root.set("version", "1.0.0")

        info_tributaria = et.SubElement(root, "infoTributaria")
        ambiente = et.SubElement(info_tributaria, "ambiente")
        ambiente.text = str(ambiente_value)

        tipo_emision = et.SubElement(info_tributaria, "tipoEmision")
        tipo_emision.text = str(tipo_emision_value)

        razon_social = et.SubElement(info_tributaria, "razonSocial")
        razon_social.text = cadenas.strip(datos_factura['alm_razsoc'])

        nombre_comercial = et.SubElement(info_tributaria, "nombreComercial")
        nombre_comercial.text = cadenas.strip(datos_factura['alm_nomcomercial'])

        ruc = et.SubElement(info_tributaria, "ruc")
        ruc.text = cadenas.strip((datos_factura['alm_ruc']))

        clave_acceso_value = self.get_clave_acceso(datos_factura=datos_factura, tipo_ambiente=str(ambiente_value))
        clave_acceso = et.SubElement(info_tributaria, "claveAcceso")
        clave_acceso.text = clave_acceso_value

        cod_doc = et.SubElement(info_tributaria, "codDoc")
        cod_doc.text = ctes_facte.COD_DOC_FACTURA

        estab = et.SubElement(info_tributaria, "estab")
        estab.text = str(datos_factura['alm_numest'])

        pto_emi = et.SubElement(info_tributaria, "ptoEmi")
        pto_emi.text = str(datos_factura['tdv_numero'])

        secuencial = et.SubElement(info_tributaria, "secuencial")
        trn_compro = datos_factura['trn_compro']

        secuencial_value = trn_compro[6:]
        secuencial.text = secuencial_value

        alm_matriz_value = datos_alm_matriz['alm_direcc']

        dir_matriz = et.SubElement(info_tributaria, "dirMatriz")
        dir_matriz.text = alm_matriz_value

        info_factura = et.SubElement(root, "infoFactura")

        fecha_emision = et.SubElement(info_factura, "fechaEmision")
        fecha_emision.text = datos_factura['trn_fecreg']

        dir_establecimiento = et.SubElement(info_factura, "dirEstablecimiento")
        dir_establecimiento.text = datos_factura['alm_direcc']

        cnt_codigo = datos_alm_matriz['cnt_codigo']
        if cnt_codigo > 0:
            contribuyente_especial = et.SubElement(info_factura, "contribuyenteEspecial")
            contribuyente_especial.text = str(cnt_codigo)

        alm_contab = datos_alm_matriz['alm_contab']
        if alm_contab:
            obligado_contab = et.SubElement(info_factura, "obligadoContabilidad")
            obligado_contab.text = ctes_facte.SI

        tipoidentcomprador_value = self.get_tipo_ident_comprador(per_codigo=datos_factura['per_codigo'],
                                                                 per_ciruc=datos_factura['per_ciruc'])
        tipo_ident_comprador = et.SubElement(info_factura, "tipoIdentificacionComprador")
        tipo_ident_comprador.text = str(tipoidentcomprador_value)

        razon_social_comprador = et.SubElement(info_factura, "razonSocialComprador")
        razon_social_comprador.text = cadenas.clean_for_rentas(cadenas.strip_upper(datos_factura['per_nomapel']))[0:300]

        identificacion_comprador = et.SubElement(info_factura, "identificacionComprador")
        identificacion_comprador.text = cadenas.strip(datos_factura['per_ciruc'])[0:20]

        if cadenas.es_nonulo_novacio(datos_factura['per_direccion']):
            direccion_comprador = et.SubElement(info_factura, "direccionComprador")
            direccion_comprador.text = cadenas.clean_for_rentas(cadenas.strip(datos_factura['per_direccion']))[0:300]

        total_sin_impuestos = et.SubElement(info_factura, "totalSinImpuestos")
        total_sin_impuestos.text = str(numeros.roundm2(totales['total_sin_impuesto']))

        total_descuento = et.SubElement(info_factura, "totalDescuento")
        total_descuento.text = str(numeros.roundm2(totales['total_descuentos']))

        total_con_impuestos = et.SubElement(info_factura, "totalConImpuestos")
        total_impuesto = et.SubElement(total_con_impuestos, "totalImpuesto")

        codigo_impuesto_item = et.SubElement(total_impuesto, "codigo")
        codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

        codigo_porcentaje = et.SubElement(total_impuesto, "codigoPorcentaje")
        codigo_porcentaje.text = ctes_facte.CODIGO_IVA_15

        base_imponible = et.SubElement(total_impuesto, "baseImponible")
        base_imponible.text = str(numeros.roundm2(totales['base_imp_iva_15']))

        valor_impuesto = et.SubElement(total_impuesto, "valor")
        valor_impuesto.text = str(numeros.roundm2(totales['impuesto_iva_15']))

        if totales['base_imp_iva_5'] > 0:
            total_impuesto_5 = et.SubElement(total_con_impuestos, "totalImpuesto")

            codigo_impuesto_item = et.SubElement(total_impuesto_5, "codigo")
            codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

            codigo_porcentaje = et.SubElement(total_impuesto_5, "codigoPorcentaje")
            codigo_porcentaje.text = ctes_facte.CODIGO_IVA_5

            base_imponible = et.SubElement(total_impuesto_5, "baseImponible")
            base_imponible.text = str(numeros.roundm2(totales['base_imp_iva_5']))

            valor_impuesto = et.SubElement(total_impuesto_5, "valor")
            valor_impuesto.text = str(numeros.roundm2(totales['impuesto_iva_5']))

        propina = et.SubElement(info_factura, "propina")
        propina.text = str(numeros.roundm2(datos_factura['propina']))

        importe_total_value = numeros.roundm2(totales['total'])
        importe_total = et.SubElement(info_factura, "importeTotal")
        importe_total.text = str(importe_total_value)

        moneda = et.SubElement(info_factura, "moneda")
        moneda.text = ctes_facte.MONEDA

        pagos = et.SubElement(info_factura, "pagos")

        # total_pago_efectivo_value = numeros.roundm2(totales['pago_efectivo'])
        # total_pago_credito_value = numeros.roundm2(totales['pago_credito'])

        codigo_forma_pago = self.get_forma_pago(pagos_db)

        pago_efectivo = et.SubElement(pagos, "pago")
        codigo_forma_pago_efec = et.SubElement(pago_efectivo, "formaPago")
        codigo_forma_pago_efec.text = codigo_forma_pago

        total_forma_pago_efec = et.SubElement(pago_efectivo, "total")
        total_forma_pago_efec.text = str(importe_total_value)

        # TODO: En esta caso se debe agregar tambien las etiquetes de plazo y unidad de tiempo, por el momento solo se deja el pago sin utilizacion del sistema financiero
        """
        if total_pago_credito_value > 0:
            pago_credito = et.SubElement(pagos, "pago")
            codigo_forma_pago_cre = et.SubElement(pago_credito, "formaPago")
            codigo_forma_pago_cre.text = ctes_facte.PAGO_OTROS_SIN_UTILIZACION

            total_forma_pago_cre = et.SubElement(pago_credito, "total")
            total_forma_pago_cre.text = str(total_pago_credito_value)
        """

        detalles = et.SubElement(root, "detalles")

        for detalle_db in detalles_db:
            detalle_item = et.SubElement(detalles, "detalle")

            codigo_principal_item = et.SubElement(detalle_item, "codigoPrincipal")
            codigo_principal_item.text = cadenas.clean_for_rentas(cadenas.strip(detalle_db['ic_code']))[0:25]

            descripcion_item = et.SubElement(detalle_item, "descripcion")
            descripcion_item.text = cadenas.clean_for_rentas(cadenas.strip_upper(detalle_db['ic_nombre']))[0:300]

            cantidad_item = et.SubElement(detalle_item, "cantidad")
            cantidad_item.text = str(numeros.roundm2(detalle_db['dt_cant']))

            precio_unitario_item = et.SubElement(detalle_item, "precioUnitario")
            precio_unitario_item.text = str(numeros.roundm2(detalle_db['dt_precio']))

            descuento_fila_val = (detalle_db['dt_decto'] * detalle_db['dt_cant']) + detalle_db['dt_dectogen']
            descuento_fila_round = numeros.roundm2(descuento_fila_val)

            descuento_item = et.SubElement(detalle_item, "descuento")
            descuento_item.text = str(descuento_fila_round)

            precio_total_sin_impuesto_val = detalle_db['subtotal'] - descuento_fila_val

            precio_total_sin_impuesto_item = et.SubElement(detalle_item, "precioTotalSinImpuesto")
            precio_total_sin_impuesto_item.text = str(numeros.roundm2(precio_total_sin_impuesto_val))

            impuestos = et.SubElement(detalle_item, "impuestos")
            impuesto_item = et.SubElement(impuestos, "impuesto")

            codigo_impuesto_item = et.SubElement(impuesto_item, "codigo")
            codigo_impuesto_item.text = ctes_facte.CODIGO_IMPUESTO_IVA

            dt_cant = detalle_db['dt_cant']
            dai_impg = detalle_db['dai_impg']
            dai_impg_mult = numeros.roundm2(dai_impg * 100)
            dt_decto = detalle_db['dt_decto']
            dt_decto_cant = dt_decto * dt_cant
            if detalle_db['dt_valdto'] >= 0.0:
                dt_decto_cant = dt_decto
            dt_dectogen = detalle_db['dt_dectogen']
            dt_precio = detalle_db['dt_precio']
            subtforiva = (dt_cant * dt_precio) - (dt_decto_cant + dt_dectogen)

            # subt = (detalle_db['dt_cant'] * detalle_db['dt_precio']) - detalle_db['dt_valdto']

            if dai_impg > 0:
                ivaval = numeros.get_valor_iva(subtforiva, dai_impg)
                codigo_porcentaje_impuesto_item = et.SubElement(impuesto_item, "codigoPorcentaje")
                if dai_impg == 0.05:
                    codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_5
                else:
                    codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_15
                tarifa_impuesto_item = et.SubElement(impuesto_item, "tarifa")
                tarifa_impuesto_item.text = str(dai_impg_mult)
                base_imponible_impuesto_item = et.SubElement(impuesto_item, "baseImponible")
                base_imponible_impuesto_item.text = str(numeros.roundm2(subtforiva))
                valor_impuesto_item = et.SubElement(impuesto_item, "valor")
                valor_impuesto_item.text = str(numeros.roundm2(ivaval))
            else:
                codigo_porcentaje_impuesto_item = et.SubElement(impuesto_item, "codigoPorcentaje")
                codigo_porcentaje_impuesto_item.text = ctes_facte.CODIGO_IVA_CERO
                tarifa_impuesto_item = et.SubElement(impuesto_item, "tarifa")
                tarifa_impuesto_item.text = "0.00"
                base_imponible_impuesto_item = et.SubElement(impuesto_item, "baseImponible")
                base_imponible_impuesto_item.text = str(numeros.roundm2(subtforiva))
                valor_impuesto_item = et.SubElement(impuesto_item, "valor")
                valor_impuesto_item.text = "0.00"

        xml_str = et.tostring(root, encoding='utf8').decode('utf8')

        return {
            'clave': clave_acceso_value,
            'xml': xml_str
        }
        # return xml_str
