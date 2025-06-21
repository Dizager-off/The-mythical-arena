from __future__ import annotations
import math
import pygame
import audio
from model.enemy import Enemy
from model.effects import DeathEffect
import settings


def _update_player(game: "GameController") -> list[pygame.Rect]:
    old_pos = game.player.rect.topleft
    game.player.update(game.input.keys or pygame.key.get_pressed())
    blocks = game.map.collides + ([] if game.door_open else game.map.door_collides)
    if any(game.player.collision_rect().colliderect(r) for r in blocks):
        game.player.rect.topleft = old_pos
    for dx, dy in game.input.shoot_dirs:
        game.pbul += game.player.shoot(dx, dy)
    return blocks


def _update_bullets(game: "GameController", blocks: list[pygame.Rect]) -> None:
    screen_rect = pygame.Rect(0, 0, settings.SCREEN_W, settings.SCREEN_H)
    for lst in (game.pbul, game.ebul):
        for b in lst[:]:
            b.update()
            hit_wall = any(b.rect().colliderect(r) for r in blocks)
            off = not screen_rect.colliderect(b.rect().move(-game.cam[0], -game.cam[1]))
            if hit_wall or b.off_world() or off:
                lst.remove(b)


def _update_effects(game: "GameController") -> None:
    for eff in game.effects[:]:
        eff.update()
        if eff.done():
            game.effects.remove(eff)


def _enemy_tree(game: "GameController") -> None:
    game.enemy_tree.clear()
    for z in game.wave_mgr.enemies:
        game.enemy_tree.insert(z, z.collision_rect())


def _check_orbitals(game: "GameController") -> None:
    for ang in game.player.orbital_angles():
        cx = game.player.rect.centerx + settings.ORBITAL_RADIUS * math.cos(ang)
        cy = game.player.rect.centery + settings.ORBITAL_RADIUS * math.sin(ang)
        rect = pygame.Rect(
            cx - settings.ORBITAL_HITBOX,
            cy - settings.ORBITAL_HITBOX,
            settings.ORBITAL_HITBOX * 2,
            settings.ORBITAL_HITBOX * 2,
        )
        for z in game.enemy_tree.query(rect):
            z_rad = getattr(z, "radius", getattr(z, "RADIUS", 0))
            if math.hypot(z.x - cx, z.y - cy) < z_rad + settings.ORBITAL_HITBOX:
                if isinstance(z, Enemy):
                    audio.KILL_ENEMY.play()
                    game.effects.append(DeathEffect(z.x, z.y, z.death_frames()))
                if z in game.wave_mgr.enemies:
                    game.wave_mgr.enemies.remove(z)


def _update_enemies(game: "GameController", blocks: list[pygame.Rect]) -> None:
    margin = settings.ENEMY_UPDATE_MARGIN
    for z in game.wave_mgr.enemies[:]:
        r = z.rect().move(-game.cam[0], -game.cam[1])
        off = (
            r.right < -margin
            or r.left > settings.SCREEN_W + margin
            or r.bottom < -margin
            or r.top > settings.SCREEN_H + margin
        )
        if off:
            continue
        game._enemy_step(z, blocks)


def _check_transitions(game: "GameController") -> None:
    if game.input.teleport:
        game._teleport_shop()
        return
    if game.wave_mgr.cleared() and not game.door_open:
        audio.DOOR_OPEN.play()
        game.door_open = True
    if game.door_open and any(
        game.player.collision_rect().colliderect(r) for r in game.map.door_collides
    ):
        if game.wave_mgr.wave == settings.TOTAL_WAVES:
            from view.rooms import Rooms
            Rooms.victory_screen(game.surf)
            game.running = False
            return
        game._teleport_shop()
    if game.player.lives <= 0:
        from view.rooms import Rooms
        Rooms.game_over_screen(game.surf)
        game.running = False


def process_arena(game: "GameController") -> None:
    blocks = _update_player(game)
    _update_bullets(game, blocks)
    _update_effects(game)
    game.wave_mgr.update()
    _enemy_tree(game)
    _check_orbitals(game)
    _update_enemies(game, blocks)
    game._bullet_collisions()
    _check_transitions(game)
