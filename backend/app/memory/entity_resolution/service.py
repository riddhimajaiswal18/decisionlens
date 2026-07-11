"""Two-stage entity resolution implementation."""

from backend.app.memory.entity_resolution.interfaces import EntityCanonicalizer, EntityResolver
from backend.app.memory.entity_resolution.models import EntityResolutionConfig, ResolvedEntity


class DefaultEntityResolver(EntityResolver):
    """Uses injected LLM canonicalization followed by deterministic configured aliases."""

    def __init__(self, canonicalizer: EntityCanonicalizer, *, config: EntityResolutionConfig | None = None) -> None:
        self._canonicalizer = canonicalizer
        self._config = config or EntityResolutionConfig()

    async def resolve(self, names: list[str]) -> list[ResolvedEntity]:
        return [
            ResolvedEntity(original_name=name, canonical_name=await self.canonicalize(name))
            for name in names
            if name.strip()
        ]

    async def canonicalize(self, name: str) -> str:
        proposed = await self._canonicalizer.canonicalize(name)
        return self.normalize(proposed or name)

    def normalize(self, name: str) -> str:
        key = name.strip().casefold()
        return self._config.lookup_map.get(key, name.strip())
