import { EntityType, SelectedEntity, SettingsModule } from '@/store/modules/settings'
import { DisplayedLesson, getLessonId, StorageModule } from '@/store/modules/storage'

export function getTimetableData (entity: SelectedEntity | null, days: number[]): Map<number, Map<number, DisplayedLesson>> {
  const dataSource = entity?.type !== EntityType.EmptyClassrooms ? StorageModule.timetable : StorageModule.emptyClassrooms
  const substitutionsSource = entity?.type === EntityType.Class ? new Map(StorageModule.substitutions) : new Map()

  const displayedLessons: Map<number, Map<number, DisplayedLesson>> = new Map()
  for (const lesson of dataSource || []) {
    // Check if class/teacher/classroom is correct
    let isCorrectEntity = false
    if (entity?.type === EntityType.Class) {
      isCorrectEntity = entity.data.includes(lesson.class)
    } else if (entity?.type === EntityType.Teacher) {
      isCorrectEntity = entity.data.includes(lesson.teacher)
    } else if (entity?.type === EntityType.Classroom) {
      isCorrectEntity = entity.data.includes(lesson.classroom)
    } else if (entity?.type === EntityType.EmptyClassrooms) isCorrectEntity = true

    if (!days.includes(lesson.day) || !isCorrectEntity) continue

    // Convert data into structured format
    if (!displayedLessons.has(lesson.day)) {
      displayedLessons.set(lesson.day, new Map())
    }

    if (!displayedLessons.get(lesson.day)?.has(lesson.time)) {
      displayedLessons.get(lesson.day)?.set(lesson.time, {
        day: lesson.day,
        time: lesson.time,
        subjects: [],
        classes: [],
        teachers: [],
        classrooms: [],
        substitution: false
      })
    }

    // TODO: Add support for substitutions for teachers and classrooms

    // Add substitution if it exists
    // Currently only works for classes
    if (SettingsModule.showSubstitutions && substitutionsSource.has(getLessonId(lesson))) {
      for (const substitution of substitutionsSource.get(getLessonId(lesson))) {
        if (substitution.subject) {
          /* eslint-disable no-unused-expressions */
          displayedLessons.get(lesson.day)?.get(lesson.time)?.subjects.push(substitution.subject)
          displayedLessons.get(lesson.day)?.get(lesson.time)?.classes.push(substitution.class)
          displayedLessons.get(lesson.day)?.get(lesson.time)?.teachers.push(substitution.teacher)
          displayedLessons.get(lesson.day)?.get(lesson.time)?.classrooms.push(substitution.classroom)
          /* eslint-enable */
        }

        const displayedLesson = displayedLessons.get(lesson.day)?.get(lesson.time)
        if (displayedLesson) displayedLesson.substitution = true
      }

      substitutionsSource.delete(getLessonId(lesson))
      continue
    }

    /* eslint-disable no-unused-expressions */
    displayedLessons.get(lesson.day)?.get(lesson.time)?.subjects.push(lesson.subject)
    displayedLessons.get(lesson.day)?.get(lesson.time)?.classes.push(lesson.class)
    displayedLessons.get(lesson.day)?.get(lesson.time)?.teachers.push(lesson.teacher)
    displayedLessons.get(lesson.day)?.get(lesson.time)?.classrooms.push(lesson.classroom)
    /* eslint-enable */
  }

  // Add substitutions for new lessons
  if (SettingsModule.showSubstitutions) {
    for (const substitutionList of substitutionsSource.values()) {
      // Check if class/teacher/classroom is correct
      let isCorrectEntity = false
      if (entity?.type === EntityType.Class) {
        isCorrectEntity = entity.data.includes(substitutionList[0].class)
      } else if (entity?.type === EntityType.Teacher) {
        isCorrectEntity = entity.data.includes(substitutionList[0].teacher)
      } else if (entity?.type === EntityType.Classroom) {
        isCorrectEntity = entity.data.includes(substitutionList[0].classroom)
      } else if (entity?.type === EntityType.EmptyClassrooms) isCorrectEntity = true

      if (!days.includes(substitutionList[0].day) || !isCorrectEntity) continue

      // Convert data into structured format
      if (!displayedLessons.has(substitutionList[0].day)) {
        displayedLessons.set(substitutionList[0].day, new Map())
      }

      if (!displayedLessons.get(substitutionList[0].day)?.has(substitutionList[0].time)) {
        displayedLessons.get(substitutionList[0].day)?.set(substitutionList[0].time, {
          day: substitutionList[0].day,
          time: substitutionList[0].time,
          subjects: [],
          classes: [],
          teachers: [],
          classrooms: [],
          substitution: true
        })
      }

      for (const substitution of substitutionList) {
        /* eslint-disable no-unused-expressions */
        displayedLessons.get(substitution.day)?.get(substitution.time)?.subjects.push(substitution.subject)
        displayedLessons.get(substitution.day)?.get(substitution.time)?.classes.push(substitution.class)
        displayedLessons.get(substitution.day)?.get(substitution.time)?.teachers.push(substitution.teacher)
        displayedLessons.get(substitution.day)?.get(substitution.time)?.classrooms.push(substitution.classroom)
        /* eslint-enable */
      }
    }
  }

  return displayedLessons
}
