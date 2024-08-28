import { EntityType } from '@/stores/settings'

/**
 * Returns the timetable route properties for the specified entity.
 */
export function generateTimetableRoute(
  entityType: EntityType,
  entityList: string[],
  replace: boolean = false,
) {
  let paramType
  let paramValue = entityList.join(',')

  switch (entityType) {
    case EntityType.Class:
      paramType = 'classes'
      break
    case EntityType.Teacher:
      paramType = 'teachers'
      break
    case EntityType.Classroom:
      paramType = 'classrooms'
      break
    case EntityType.EmptyClassrooms:
      paramType = 'classrooms'
      paramValue = 'empty'
  }

  return {
    name: 'timetable',
    params: { type: paramType, value: paramValue },
    replace,
  }
}
