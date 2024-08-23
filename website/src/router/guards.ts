import { storeToRefs } from 'pinia'
import type { NavigationGuardReturn, RouteLocationNormalizedGeneric } from 'vue-router'

import { useListsStore } from '@/stores/lists'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import { generateTimetableRoute } from '@/utils/router'

export function homeGuard(): NavigationGuardReturn {
  const { entityType } = useSettingsStore()

  // Redirect the user either to the timetable or welcome page
  if (entityType === EntityType.None) return { name: 'welcome', replace: true }
  else return { name: 'timetable', replace: true }
}

export function welcomeGuard(): NavigationGuardReturn {
  const { entityType } = useSettingsStore()

  // Redirect the user to the timetable page if it has the entity set
  if (entityType !== EntityType.None) return { name: 'timetable', replace: true }
}

export async function timetableGuard(
  route: RouteLocationNormalizedGeneric,
  source: RouteLocationNormalizedGeneric,
): Promise<NavigationGuardReturn> {
  const sessionStore = useSessionStore()
  const { currentEntityType, currentEntityList } = storeToRefs(sessionStore)
  const { resetEntityToSettings } = sessionStore

  const listsStore = useListsStore()
  const { classesList, teachersList, classroomsList } = storeToRefs(listsStore)
  const { updateLists } = listsStore

  if (!route.params.type) {
    // We only want to replace routes if coming from home
    const replace = source.name === 'home'

    if (currentEntityType.value === EntityType.None) {
      // The entity is not stored yet, show the welcome page
      return { name: 'welcome', replace }
    }

    // Load the stored entity from settings
    resetEntityToSettings()

    // Navigate to the correct timetable page
    return generateTimetableRoute(currentEntityType.value, currentEntityList.value, true)
  }

  if (route.params.value) {
    // Try to get an entity based on the route params
    const routeType = route.params.type as string
    const routeValue = (route.params.value as string).split(',')

    // Update the entity lists asynchronously
    const updatingLists = updateLists()

    // Only wait until lists are ready if they have not been set yet
    // This improves load performance but has a small possibility of outdated lists
    // This should not matter much because it lists should not frequently change
    if (!classesList.value.length || !teachersList.value.length || !classesList.value.length) {
      await updatingLists
    }

    // If the entity matches correctly, set it in the session
    if (
      routeType === 'classes' && //
      routeValue.some(elem => classesList.value.includes(elem))
    ) {
      currentEntityType.value = EntityType.Class
      currentEntityList.value = routeValue
      return
    } else if (
      routeType === 'teachers' && //
      routeValue.some(elem => teachersList.value.includes(elem))
    ) {
      currentEntityType.value = EntityType.Teacher
      currentEntityList.value = routeValue
      return
    } else if (
      routeType === 'classrooms' && //
      routeValue.some(elem => classroomsList.value.includes(elem))
    ) {
      currentEntityType.value = EntityType.Classroom
      currentEntityList.value = routeValue
      return
    } else if (
      routeType === 'classrooms' && //
      routeValue.length === 1 && //
      routeValue[0] === 'empty'
    ) {
      currentEntityType.value = EntityType.EmptyClassrooms
      currentEntityList.value = ['Proste učilnice']
      return
    }
  }

  // We could not get a valid entity from params
  return {
    name: 'notFound',
    params: { pathMatch: route.path.substring(1).split('/') },
    query: route.query,
    hash: route.hash,
    replace: true,
  }
}
