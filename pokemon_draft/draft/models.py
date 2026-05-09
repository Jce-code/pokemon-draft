from django.db import models
from django.utils import timezone

class DraftState(models.Model):
    started = models.BooleanField(default=False)
    current_pick_number = models.IntegerField(default=1)
    turn_started_at = models.DateTimeField(default=timezone.now)
    max_legendaries = models.IntegerField(default=1)
    max_mythicals = models.IntegerField(default=0)
    max_paradox = models.IntegerField(default=1)
    max_ultra_beasts = models.IntegerField(default=1)
    pick_timer_seconds = models.IntegerField(default=90)
    

    def __str__(self):
        return "Main Draft"


class Player(models.Model):
    name = models.CharField(max_length=100)
    draft_position = models.IntegerField()

    def __str__(self):
        return self.name


class DraftPokemon(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField()
    category = models.CharField(max_length=50)
    picked_by = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)
    pick_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name