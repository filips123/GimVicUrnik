import { EntityType } from '@/stores/settings'

/**
 * Sorts entities based on their type and name.
 *
 * Real classes are sorted first, then followed by other classes.
 * All classes are sorted alphabetically with basic ASCII comparison.
 *
 * Teachers are sorted alphabetically with proper locale comparison.
 *
 * Other entities are sorted alphabetically with basic ASCII comparison.
 */
export function sortEntities(type: EntityType, entities: string[]): string[] {
  return entities.sort((entity1, entity2) => {
    if (type === EntityType.Class) {
      // Real classes (with two letters) should be first and sorted alphabetically
      // Then, other classes should follow, also sorted alphabetically
      if ((entity1.length === 2) !== (entity2.length === 2)) return entity1.length === 2 ? -1 : 1
    }

    if (type === EntityType.Teacher) {
      // Sort teachers alphabetically with proper locale comparison
      return entity1.localeCompare(entity2, 'sl')
    }

    // Sort other entities with basic comparison
    return entity1 < entity2 ? -1 : 1
  })
}
