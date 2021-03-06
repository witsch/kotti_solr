from kotti.resources import Document, get_root
from datetime import datetime, timedelta
from mock import Mock


def test_index_document(solr, db_session):
    now = datetime.now()
    doc = Document(title='foo', body=u'bar!', modification_date=now)
    doc.id = 23     # we don't really add the object yet...
    from kotti_solr.events import add_document_handler
    request = Mock(resource_path=lambda _: '/path/')
    add_document_handler(event=Mock(object=doc, request=request))
    results = list(solr.query(title='foo'))
    assert len(results) == 1
    assert results[0]['id'] == 'document-23'
    assert results[0]['path'] == '/path/'
    # Solr's date values don't take microseconds into account...
    assert abs(results[0]['modification_date'] - now) < timedelta(milliseconds=1)


def test_add_document_triggers_indexing(solr, db_session, request):
    get_root()['doc'] = Document(title=u'foo', body=u'bar!', description=u'foo!')
    db_session.flush()
    results = list(solr.query(title='foo'))
    assert len(results) == 1
    assert results[0]['description'] == 'foo!'
    assert results[0]['path'] == request.resource_path(get_root()['doc'])
