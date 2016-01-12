from search.searchers.instagram import MediaSearchInstagram
from search.searchers.vkontakte import MediaSearchVK
# from search.searchers.youtube import MediaSearchYouTube
from search.searchers.podacisearcher import DocumentSearchPodaci
from search.searchers.datatracker import DocumentSearchDataTracker
from search.searchers.opencorporates import EntitySearchOpenCorporates

SEARCHERS = [MediaSearchInstagram, MediaSearchVK,  # MediaSearchYouTube,
             DocumentSearchPodaci, EntitySearchOpenCorporates,
             DocumentSearchDataTracker]
