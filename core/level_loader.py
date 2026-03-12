import json
import os

import pygame

from core.asset_manager import AssetManager


class LevelLoader:
    """Charge et interprète les fichiers json (LDtk) pour générer le monde de jeu."""

    def __init__(self, phase):
        self.phase = phase

    def load_level(self, file_path: str, level_index: int = 0) -> None:
        """Méthode principale de chargement."""
        data = self._load_json(file_path)
        if not data:
            return

        # 1. Préparation du Tileset et du niveau
        tileset_img = self._get_tileset_image(data)
        level_data = data["levels"][level_index]

        lvl_w, lvl_h = level_data["pxWid"], level_data["pxHei"]
        level_surface = pygame.Surface((lvl_w, lvl_h), pygame.SRCALPHA)

        # 2. Traitement des calques (du bas vers le haut)
        for layer in reversed(level_data.get("layerInstances", [])):
            self._process_layer(layer, level_surface, tileset_img)

        # 3. Finalisation et injection dans la phase
        self.phase.level_image = level_surface
        self.phase.level_mask = pygame.mask.from_surface(level_surface)

        print(f"Level '{level_data['identifier']}' loaded successfully.")

    def _load_json(self, file_path: str) -> dict:
        """Ouvre et lit le fichier LDtk."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to open level file: {e}")
            return None

    def _get_tileset_image(self, data: dict) -> pygame.Surface:
        """Extrait l'image du tileset via l'AssetManager."""
        try:
            tileset_data = data["defs"]["tilesets"][0]
            image_name = os.path.basename(tileset_data["relPath"]).split(".")[0]
            return AssetManager.get_image(image_name)
        except (KeyError, IndexError) as e:
            print(f"Tileset definition error: {e}")
            return None

    def _process_layer(
        self, layer: dict, surface: pygame.Surface, tileset_img: pygame.Surface
    ) -> None:
        """Identifie le type de calque et délègue le travail."""
        name = layer.get("__identifier", "")

        if name == "Collision":
            self._render_tiles(layer, surface, tileset_img)

        elif name == "Entities":
            self._spawn_entities(layer)

    def _render_tiles(
        self, layer: dict, surface: pygame.Surface, tileset_img: pygame.Surface
    ) -> None:
        """Dessine les tuiles sur la surface du niveau."""
        tiles = layer.get("gridTiles", []) + layer.get("autoLayerTiles", [])
        grid_size = layer["__gridSize"]

        for tile in tiles:
            world_x, world_y = tile["px"]
            src_x, src_y = tile["src"]

            # Utilisation de subsurface pour découper la tuile dans le tileset
            tile_rect = pygame.Rect(src_x, src_y, grid_size, grid_size)
            tile_surf = tileset_img.subsurface(tile_rect)
            surface.blit(tile_surf, (world_x, world_y))

    def _spawn_entities(self, layer: dict) -> None:
        """Gère le placement des entités spéciales."""
        for entity in layer.get("entityInstances", []):
            if entity["__identifier"] == "Spawn_pos":
                x, y = entity["px"]
                self._teleport_player(x, y)

    def _teleport_player(self, x: int, y: int) -> None:
        """Positionne le joueur et synchronise son moteur physique."""
        player = self.phase.player
        player.rect.midbottom = (x, y)

        if hasattr(player, "movable"):
            player.movable.pos = pygame.Vector2(player.rect.topleft)
