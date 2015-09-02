from id.apis.elastic import elastic

from search.searchers.base import DocumentSearcher, ResultSet
from search.searchers.base import DocumentSearchResult


class DocumentSearchPodaci(DocumentSearcher):
    PROVIDER = "Podaci"

    def search(self, **kwargs):
        # offset=kwargs.get("offset", 0)
        results = elastic.search(term=kwargs["q"], index='id_prod', limit=50)
        result_count = results['hits']['total']
        resultset = ResultSet(total=result_count)
        for r in results['hits']['hits']:
            text = "<br/>".join(r["highlight"]["text"])
            i = DocumentSearchResult(self.PROVIDER,
                                    r["fields"]["url"],
                                    r["fields"]["date_added"], text,
                                    r["fields"]["title"], metadata=r)
            resultset.append(i)
        return resultset # results['hits']['hits']
