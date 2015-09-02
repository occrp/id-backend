from search.searchers.base import DocumentSearcher


class EntitySearchOpenCorporates(DocumentSearcher):
    PROVIDER = "OpenCorporates"
    SEARCHER = opencorporates.OpenCorpSearch()

    def search(self, q, offset=0, limit=100, **kwargs):
        results = self.SEARCHER.search(q, offset, limit)
        self.result_count = results.resultcount
        return results.resultdata
