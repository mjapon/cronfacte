# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler

import requests

from setup.models.conf import BaseDao
from setup.utils import ctes_facte

rutalogs = "/var/log/cronface.log"

logging.basicConfig(handlers=[RotatingFileHandler(filename=rutalogs,
                                                  mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                    format='%(levelname)s %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y%I:%M:%S %p')

log = logging.getLogger(__name__)


class NotifCompeUtil(BaseDao):
    # APP_GMAIL_CODE_MANUEL = "jqzanuuvwnthhonx"
    APP_GMAIL_CODE = "aavhytlcnuspkmti"

    def attach_file_to_email(self, email_message, filename, path):
        # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
        with open(path, "rb") as f:
            file_attachment = MIMEApplication(f.read())
        # Add header/name to the attachments
        file_attachment.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        # Attach the file to the message
        email_message.attach(file_attachment)

    def attach_bytes_to_email(self, email_message, filename, bytesresponse):
        file_attachment = MIMEApplication(bytesresponse)
        file_attachment.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        # Attach the file to the message
        email_message.attach(file_attachment)

    def get_datos_alm_matriz(self, sec_codigo):
        sqlbase = """
        select  alm.alm_codigo,
                alm_numest,
                alm_razsoc,
                alm_descri,
                alm_direcc,
                alm_repleg,
                alm_email,
                alm_websit,
                alm_fono1,
                alm_fono2,
                alm_movil,
                alm_ruc,
                alm_ciudad,
                alm_sector,
                alm_fecreg,
                cnt_codigo,
                alm_matriz,
                alm_tipoamb,
                alm_nomcomercial,
                alm_contab from talmacen alm
        """

        where = " where alm_matriz = 1 "
        if int(sec_codigo) > 1:
            where = """
            join tseccion sec on alm.alm_codigo = sec.alm_codigo 
            where sec.sec_id = {0}
            """.format(sec_codigo)

        sql = "{0} {1}".format(sqlbase, where)

        tupla_desc = (
            'alm_codigo',
            'alm_numest',
            'alm_razsoc',
            'alm_descri',
            'alm_direcc',
            'alm_repleg',
            'alm_email',
            'alm_websit',
            'alm_fono1',
            'alm_fono2',
            'alm_movil',
            'alm_ruc',
            'alm_ciudad',
            'alm_sector',
            'alm_fecreg',
            'cnt_codigo',
            'alm_matriz',
            'alm_tipoamb',
            'alm_nomcomercial',
            'alm_contab'
        )

        return self.first(sql, tupla_desc)

    def get_datos_for_notif(self, trn_codigo):
        sql = """
        select per.per_id, per.per_nombres||' '||coalesce(per.per_apellidos,'') as referente,
        per.per_ciruc, alm.alm_razsoc, alm.alm_nomcomercial, per.per_email, asi.trn_compro, alm.alm_tipoamb, 
        alm.alm_ruc, alm.alm_direcc, asi.trn_fecreg, asifacte.tfe_claveacceso, asifacte.tfe_numautoriza, 
        asifacte.tfe_fecautoriza, asi.sec_codigo
        from
                tasiento asi
                join tasifacte asifacte on asi.trn_codigo = asifacte.trn_codigo
                join tpersona per on asi.per_codigo = per.per_id                
                join talmacen alm on alm.alm_matriz = 1
                where asi.trn_codigo = {0}
        """.format(trn_codigo)

        tupla_desc = ('per_id', 'referente', 'per_ciruc', 'alm_razsoc', 'alm_nomcomercial', 'per_email', 'trn_compro',
                      'alm_tipoamb', 'alm_ruc', 'alm_direcc', 'trn_fecreg', 'tfe_claveacceso', 'tfe_numautoriza',
                      'tfe_fecautoriza', 'sec_codigo')

        response = self.first(sql, tupla_desc)
        if response is not None:
            sec_codigo = response['sec_codigo']
            if sec_codigo > 1:
                sql = """
                select per.per_id, per.per_nombres||' '||coalesce(per.per_apellidos,'') as referente,
                per.per_ciruc, alm.alm_razsoc, alm.alm_nomcomercial, per.per_email, asi.trn_compro, alm.alm_tipoamb, 
                alm.alm_ruc, alm.alm_direcc, asi.trn_fecreg, asifacte.tfe_claveacceso, asifacte.tfe_numautoriza, 
                asifacte.tfe_fecautoriza, asi.sec_codigo
                from
                        tasiento asi
                        join tasifacte asifacte on asi.trn_codigo = asifacte.trn_codigo
                        join tpersona per on asi.per_codigo = per.per_id      
                        join tseccion sec on asi.sec_codigo = sec.sec_id
                         join talmacen alm on alm.alm_codigo = sec.alm_codigo
                        where asi.trn_codigo = {0}
                """.format(trn_codigo)
                response = self.first(sql, tupla_desc)

        return response

    def enviar_email(self, trn_codigo, claveacceso):
        # obrener el correo para envio
        datosnotif = self.get_datos_for_notif(trn_codigo=trn_codigo)
        per_id = datosnotif['per_id']

        ambiente_text = "PRUEBAS"
        alm_tipoamb = datosnotif['alm_tipoamb']
        enviar_email = per_id > 0
        if alm_tipoamb == 2:
            ambiente_text = "PRODUCCIÓN"

        style = """.img{
            width: 20%;
            height:80%;
        }

        .center {
            margin: auto;
            width: 75%;
            border: 3px solid #88024b;
            padding: 10px;
            box-shadow: 10px -10px 5px #888787;
            border-radius: 10px;
        }
                    """
        html_email = """
                        <!doctype html>
                <html lang="es">
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>MAVIL-Notificación Comprobante Electrónico</title>
                    <style>
                        {style}
                    </style>
                </head>
                <body>
                <div class="center">
    <h2>{comercio} le ha emitido una factura - {compro}</h2>
    <img src="https://mavil.site/assets/imgs/Mavil.png" class="img">
    <p>
        Estimado/a {referente}, el comercio: {comercio} le ha emitido un comprobante electrónico, el mismo que se encuentra adjunto</p>
    <p>
    <table>
        <tr>
            <td>Número:</td><td>	{compro}</td></tr>
        <tr>
            <td>Fecha:</td><td>	{fecha}</td></tr>
        <tr>
            <td>Clave de acceso:</td><td>	{clave}</td></tr>
        <tr>
            <td>Autorización:</td><td>	{clave}</td></tr>
        <tr>
            <td>Fecha de autorización:</td><td>	{fechaaut}</td></tr>
        <tr>
            <td>Ambiente:</td><td>{ambiente}</td></tr>
        <tr>
            <td>Emisor:</td><td>{comercio}</td></tr>
        <tr>
            <td>RUC del emisor:</td><td>{ruc}</td></tr>
        <tr>
            <td>Dirección del emisor:</td><td>{direccion}</td></tr></table>
    </p>
    <p>
        Si desea consultar todos sus comprobantes electrónicos lo puede hacer en <a href='https://mavil.site/loginfacte'>mavil.site</a>
    </p>
    <p>
        Atentamente,
        </p>
    <p>
        El equipo de mavil
        <a href='https://www.mavil.site'>www.mavil.site</a>
    </p>
</div>
                </body>
                </html>
        """.format(compro=datosnotif['trn_compro'],
                   referente=datosnotif['referente'],
                   comercio=datosnotif['alm_nomcomercial'],
                   ruc=datosnotif['alm_ruc'],
                   direccion=datosnotif['alm_direcc'],
                   fecha=datosnotif['trn_fecreg'],
                   fechaaut=datosnotif['tfe_fecautoriza'],
                   clave=datosnotif['tfe_claveacceso'],
                   ambiente=ambiente_text,
                   style=style)

        alm_tipoamb = datosnotif['alm_tipoamb']
        per_email = datosnotif['per_email']

        remitente = "mavil.site@gmail.com"
        destinatario = "luisninj@hotmail.com"
        if int(alm_tipoamb) == int(ctes_facte.AMBIENTE_PRODUCCION):
            destinatario = per_email

        if enviar_email:
            if len(destinatario.strip()) > 0:
                try:
                    email_message = MIMEMultipart()
                    email_message["From"] = remitente
                    email_message["To"] = destinatario
                    email_message["Subject"] = "MAVIL - Notificación Comprobante Electrónico"

                    headers = {
                        "User-Agent": "Chrome/51.0.2704.103",
                    }

                    url_ride_pdf = "{0}/{1}?fmt=pdf".format(ctes_facte.URI_RIDE_PDF, claveacceso)
                    url_ride_xml = "{0}/{1}?fmt=xml".format(ctes_facte.URI_RIDE_XML, claveacceso)

                    log.info("entro get adjuntos")
                    response = requests.get(url_ride_pdf, headers=headers)
                    email_message.attach(MIMEText(html_email, "html"))

                    response_xml = requests.get(url_ride_xml, headers=headers)

                    self.attach_bytes_to_email(email_message, '{0}.pdf'.format(datosnotif['trn_compro']),
                                               response.content)
                    self.attach_bytes_to_email(email_message, '{0}.xml'.format(datosnotif['trn_compro']),
                                               response_xml.text)

                    email_string = email_message.as_string()
                    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
                    smtp.login(remitente, self.APP_GMAIL_CODE)

                    # smtp.sendmail(remitente, destinatario, email.as_string())
                    smtp.sendmail(remitente, destinatario, email_string)
                    smtp.quit()
                    log.info("Notificacion procesada para trn_codigo: {0}, correo enviado a {1}-->".format(trn_codigo,
                                                                                                           destinatario))
                except Exception as ex:
                    log.info("Error envio correo", ex)
            else:
                log.info(
                    "Destinatario es null o vacio, no se envia notificacion para trn_codigo:{0}".format(trn_codigo))
