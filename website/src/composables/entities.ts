import { EntityType } from '@/stores/settings'

export function sortEntityList(entityType: EntityType, entityList: string[]) {
  return entityList.sort((entity1, entity2) => {
    if (entityType != EntityType.Teacher) {
      if (entity1.length < entity2.length) {
        return -1
      } else if (entity1.length > entity2.length) {
        return 1
      }
    }

    return entity1 < entity2 ? -1 : 1
  })
}
