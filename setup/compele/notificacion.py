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

import requests

from setup.models.conf import BaseDao
from setup.utils import ctes_facte

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

    def get_datos_for_notif(self, trn_codigo):
        sql = """
        select per.per_nombres||' '||coalesce(per.per_apellidos,'') as referente,
        per.per_ciruc, alm.alm_razsoc, alm.alm_nomcomercial, per.per_email, asi.trn_compro, alm.alm_tipoamb, 
        alm.alm_ruc, alm.alm_direcc, asi.trn_fecreg, asifacte.tfe_claveacceso, asifacte.tfe_numautoriza, asifacte.tfe_fecautoriza
        from
                tasiento asi
                join tasifacte asifacte on asi.trn_codigo = asifacte.trn_codigo
                join tpersona per on asi.per_codigo = per.per_id                
                join talmacen alm on alm.alm_matriz = 1
                where asi.trn_codigo = {0}
        """.format(trn_codigo)

        tupla_desc = ('referente', 'per_ciruc', 'alm_razsoc', 'alm_nomcomercial', 'per_email', 'trn_compro',
                      'alm_tipoamb', 'alm_ruc', 'alm_direcc','trn_fecreg','tfe_claveacceso','tfe_numautoriza',
                      'tfe_fecautoriza')
        return self.first(sql, tupla_desc)

    def enviar_email(self, trn_codigo, claveacceso):
        # obrener el correo para envio

        datosnotif = self.get_datos_for_notif(trn_codigo=trn_codigo)

        ambiente_text = "PRUEBAS"
        alm_tipoamb = datosnotif['alm_tipoamb']
        if alm_tipoamb == 2:
            ambiente_text = "PRODUCCIÓN"

        html_email = """
        <!doctype html>
<html lang="es">
<html>
	<head>
		<meta charset="utf-8">
    	<title>MAVIL-Notificación Comprobante Electrónico</title>
    	<style>
    		
    	</style>
	</head>
	<body>
		<div>
			<h1>MAVIL - Notificación comprobante Electrónico - {compro}</h1>
			<img src="https://mavil.site/assets/imgs/Mavil.png">
			<p>
			Estimado/a {referente}, el comercio: {comercio} le ha emitido un comprobante electrónico, el mismo que se encuentra adjunto</p>
			<br/>
			<br/>
			<p>
			
			<table>
			<tr>
			<td>
			Tipo de comprobante:</td><td>	FACTURA</td></tr>
<tr>
			<td>Número de comprobante:</td><td>	{compro}</td></tr>
<tr>
			<td>Fecha de emisión:</td><td>	{fecha}</td></tr>
<tr>
			<td>Tipo de emisión:</td><td>	NORMAL</td></tr>
<tr>
			<td>Clave de acceso:</td><td>	{clave}</td></tr>
<tr>
			<td>Número de autorización del comprobante:</td><td>	{clave}</td></tr>
<tr>
			<td>Fecha de autorización del comprobante:</td><td>	{fechaaut}</td></tr>
<tr>
			<td>Ambiente de emisión:</td><td>{ambiente}</td></tr>
<tr>
			<td>Emisor:</td><td>	{comercio}</td></tr>
<tr>
			<td>RUC del emisor:</td><td>	{ruc}</td></tr>
<tr>
			<td>Dirección del emisor:</td><td>	{direccion}</td></tr></table>

			</p>
			<br/>
			<br/>
			<p>
			Si desea consultar todos sus comprobantes electrónicos lo puede hacer en <a href='https://mavil.site/loginfacte'>mavil.site</a>
			</p>
			<br/>
			<br/>
			<p>
			Atentamente,
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
                   ambiente=ambiente_text)

        alm_tipoamb = datosnotif['alm_tipoamb']
        per_email = datosnotif['per_email']

        remitente = "mavil.site@gmail.com"
        destinatario = "luisninj@hotmail.com"
        if int(alm_tipoamb) == int(ctes_facte.AMBIENTE_PRODUCCION):
            destinatario = per_email

        if len(destinatario.strip()) > 0:
            email_message = MIMEMultipart()
            email_message["From"] = remitente
            email_message["To"] = destinatario
            email_message["Subject"] = "MAVIL - Notificación Comprobante Electrónico"

            headers = {
                "User-Agent": "Chrome/51.0.2704.103",
            }
            # Define URL of an image
            url_ride_pdf = "{0}?claveacceso={1}".format(ctes_facte.URI_RIDE_PDF, claveacceso)
            url_ride_xml = "{0}?claveacceso={1}".format(ctes_facte.URI_RIDE_XML, claveacceso)

            response = requests.get(url_ride_pdf, headers=headers)
            email_message.attach(MIMEText(html_email, "html"))

            response_xml = requests.get(url_ride_xml, headers=headers)

            self.attach_bytes_to_email(email_message, '{0}.pdf'.format(datosnotif['trn_compro']), response.content)

            self.attach_bytes_to_email(email_message, '{0}.xml'.format(datosnotif['trn_compro']), response_xml.text)

            email_string = email_message.as_string()
            smtp = smtplib.SMTP_SSL("smtp.gmail.com")
            smtp.login(remitente, self.APP_GMAIL_CODE)

            # smtp.sendmail(remitente, destinatario, email.as_string())
            smtp.sendmail(remitente, destinatario, email_string)
            smtp.quit()
            print("Notificacion procesada para trn_codigo: {0}, correo enviado a {0}-->".format(trn_codigo,
                                                                                                destinatario))
        else:
            print("Destinatario es null o vacio, no se envia notificacion para trn_codigo:{0}".format(trn_codigo))