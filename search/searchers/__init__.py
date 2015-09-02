from search.searchers.instagram import ImageSearchInstagram
from search.searchers.vkontakte import ImageSearchVK
from search.searchers.youtube import ImageSearchYouTube
from search.searchers.podaci import DocumentSearchPodaci

# FIXME: EntitySearchOpenCorporates

SEARCHERS = [ImageSearchInstagram, ImageSearchVK, ImageSearchYouTube,
             DocumentSearchPodaci]
