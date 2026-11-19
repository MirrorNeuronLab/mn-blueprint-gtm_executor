"""Aggregate delivery evidence with no contact details or message bodies."""

from datetime import datetime, timezone


def document(status):
    stamp = datetime.fromtimestamp(status['updated_at'], timezone.utc).isoformat(timespec='seconds')
    if status['status'] == 'needs_review':
        assessment = 'The execution cycle could not finish. Current delivery counts are unavailable.'
    elif status['status'] == 'stopped':
        assessment = 'The executor stopped before the cycle completed.'
    elif status.get('needs_review'):
        assessment = 'Delivery outcomes need reconciliation. Check the provider receipt before authorizing another attempt.'
    elif status.get('inbox_caught_up') is False:
        assessment = 'The inbox check is incomplete. Delivery waits for a completed check.'
    elif status.get('pending'):
        count = status['pending']
        assessment = ('One campaign approval is pending.' if count == 1 else f'{count} campaign approvals are pending.')
        assessment += ' Inspect the exact draft and recipient list in the approval request.'
    else:
        assessment = 'No pending approvals or delivery exceptions were reported for the campaigns evaluated this cycle.'
    labels = [('contacts', 'Imported contacts'), ('quarantined', 'Quarantined contacts'),
              ('pending', 'Campaigns awaiting approval'), ('sent', 'Provider-accepted recipients'),
              ('suppressed', 'Suppressed recipients'), ('needs_review', 'Recipient outcomes to reconcile')]
    rows = [[label, status[key]] for key, label in labels if key in status]
    evidence = {'type': 'table', 'columns': ['Cycle measure', 'Observed'], 'rows': rows,
                'caption': 'Aggregate records from marketing_status.json.'} if rows else {
                    'type': 'paragraph', 'text': 'This cycle supplied no aggregate delivery counts.'}
    return {'title': 'Campaign execution report', 'identity': 'Cycle snapshot · ' + stamp, 'sections': [
        {'id': 'assessment', 'title': 'Assessment', 'blocks': [{'type': 'paragraph', 'text': assessment}]},
        {'id': 'evidence', 'title': 'Evidence', 'blocks': [evidence]},
        {'id': 'coverage', 'title': 'Coverage and next review', 'blocks': [
            {'type': 'paragraph', 'text': 'Counts describe the campaigns evaluated this cycle. An accepted send can appear in later snapshots. Inbox delivery and audience response remain unverified.'},
            {'type': 'paragraph', 'text': 'Review unresolved receipts and pending approvals in their original records. Contact addresses and message content stay outside this report.'}]},
    ]}
