"""Future one-shot operational probe. This milestone never invokes this entry point."""
from .admission import prerequisites
from .render import probe_request


def operational_probe(ledger, evidence, transport, authorization=None):
    if authorization != 'separately-authorized-operational-probe':
        raise PermissionError('M010_PROBE_NOT_AUTHORIZED')
    admitted = prerequisites(evidence, ('F0', 'F1', 'F2'))
    if not admitted['passed']:
        raise PermissionError('M010_ADMISSION_BLOCKED:' + ','.join(admitted['failures']))
    request = probe_request()
    row = ledger.reserve_probe(request, evidence['pricing'], evidence)
    if row['state'] == 'COMPLETE':
        return ledger.get(row['result_hash'])
    if row['state'] == 'RESPONSE_SAVED':
        return ledger.finalize_probe()
    if row['state'] != 'RESERVED':
        raise PermissionError('M010_PROBE_SENT_NO_RESEND')
    ledger.start_probe()
    try:
        response, receipt = transport.send(request)
        return ledger.capture_probe(response, receipt)
    except BaseException:
        with ledger.transaction():
            if getattr(transport, 'last_receipt', None):
                ledger.put(transport.last_receipt, 'failed-operational-wire-receipt')
            ledger.db.execute('UPDATE m010_probe SET error=COALESCE(error,?)', ('unresolved_or_invalid',))
        raise
