"""Servicio/proveedor concreto de infraestructura para `comunicados`."""

import httpx

from app.domain.comunicados.errors import ComunicadoProviderError


def _build_html(subject: str, body: str) -> str:
    from html import escape

    subject_escaped = escape(subject)
    paragraphs = ''.join(
        f'<p style="margin:0 0 12px;line-height:1.6;color:#111827;">{escape(line)}</p>'
        for line in body.splitlines()
        if line.strip()
    )
    return (
        '<!doctype html><html><body style="font-family:Arial,sans-serif;background:#f9fafb;padding:24px;">'
        '<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center">'
        '<table role="presentation" width="640" cellspacing="0" cellpadding="0" style="background:#ffffff;border-radius:8px;padding:24px;">'
        f'<tr><td><h2 style="margin:0 0 16px;color:#111827;">{subject_escaped}</h2>{paragraphs}</td></tr>'
        '</table></td></tr></table></body></html>'
    )


class ResendEmailProvider:
    def __init__(self, *, api_key: str, timeout_seconds: int = 20) -> None:
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def send(self, *, from_email: str, to: list[str], bcc: list[str], subject: str, body: str) -> str | None:
        with httpx.Client(timeout=self._timeout_seconds) as client:
            response = client.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {self._api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'from': from_email,
                    'to': to,
                    'bcc': bcc,
                    'subject': subject,
                    'html': _build_html(subject, body),
                },
            )

        if response.status_code >= 400:
            details = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            raise ComunicadoProviderError('Error al enviar el correo', details=details)

        payload = response.json()
        return payload.get('id')
