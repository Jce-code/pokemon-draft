from django.contrib import admin
from django.urls import path
from draft.views import generate_pokemon, start_draft, draft_board, pick_pokemon, auto_pick, join_draft, begin_draft
urlpatterns = [
    path('admin/', admin.site.urls),
    path('generate/', generate_pokemon),
    path('start-draft/', start_draft),
    path('draft-board/', draft_board),
    path('pick-pokemon/<int:pokemon_id>/', pick_pokemon),
    path('auto-pick/', auto_pick),
    path('join/', join_draft),
    path('begin-draft/', begin_draft),
]
