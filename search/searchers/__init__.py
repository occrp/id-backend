from search.searchers.instagram import ImageSearchInstagram
from search.searchers.vkontakte import ImageSearchVK
from search.searchers.youtube import ImageSearchYouTube
from search.searchers.podaci import DocumentSearchPodaci
from search.searchers.opencorporates import EntitySearchOpenCorporates

SEARCHERS = [ImageSearchInstagram, ImageSearchVK, ImageSearchYouTube,
             DocumentSearchPodaci, EntitySearchOpenCorporates]
