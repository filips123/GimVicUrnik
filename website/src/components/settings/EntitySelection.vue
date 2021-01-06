<!-- System for entity selection, used by settings and welcome pages -->

<template>
  <welcome-info v-if="currentSelectionStage === 0" :is-dialog=isDialog @clickedOk=clickedOk @closeDialog=closeDialog />

  <select-type v-else-if="currentSelectionStage === 1"
    :is-dialog=isDialog
    @closeDialog=closeDialog
    @selectedClass=selectedClassType
    @selectedClassroom=selectedClassroomType
    @selectedTeacher=selectedTeacherType />

  <select-class v-else-if="currentSelectionStage === 2" :is-dialog=isDialog @closeDialog=closeDialog />
  <select-teacher v-else-if="currentSelectionStage === 3" :is-dialog=isDialog @closeDialog=closeDialog />
  <select-classroom v-else-if="currentSelectionStage === 4" :is-dialog=isDialog @closeDialog=closeDialog />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import SelectClass from '@/components/settings/entitySelection/SelectClass.vue'
import SelectClassroom from '@/components/settings/entitySelection/SelectClassroom.vue'
import SelectTeacher from '@/components/settings/entitySelection/SelectTeacher.vue'
import SelectType from '@/components/settings/entitySelection/SelectType.vue'
import WelcomeInfo from '@/components/settings/entitySelection/WelcomeInfo.vue'
import { StorageModule } from '@/store/modules/storage'

@Component({
  components: { WelcomeInfo, SelectType, SelectClass, SelectTeacher, SelectClassroom }
})
export default class EntitySelection extends Vue {
  // -1: Close dialog
  // 0: Info and confirmation
  // 1: Type selection
  // 2: Class selection
  // 3: Teacher selection
  // 4: Classroom selection
  @Prop() initialSelectionStage!: string
  currentSelectionStage = parseInt(this.initialSelectionStage)

  @Prop() isDialog!: boolean

  // eslint-disable-next-line @typescript-eslint/no-explicit-any, no-undef
  stateHandler!: (event: WindowEventMap['popstate']) => any

  created (): void {
    StorageModule.updateLists()

    // Save handler so it can be destroyed later
    this.stateHandler = (event) => {
      if ('entitySelectionStage' in event.state) {
        this.currentSelectionStage = event.state.entitySelectionStage
      }

      if (this.currentSelectionStage === -1 && this.isDialog) {
        this.closeDialog()
      }
    }

    // Add history states so user can navigate between steps
    if (!this.isDialog) {
      history.replaceState({ entitySelectionStage: this.currentSelectionStage }, '')
    } else {
      history.replaceState({ entitySelectionStage: -1 }, '')
      history.pushState({ entitySelectionStage: this.currentSelectionStage }, '')
    }

    addEventListener('popstate', this.stateHandler)
  }

  destroyed (): void {
    removeEventListener('popstate', this.stateHandler)
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }

  clickedOk (): void {
    history.pushState({ entitySelectionStage: 1 }, '')
    this.currentSelectionStage = 1
  }

  selectedClassType (): void {
    history.pushState({ entitySelectionStage: 2 }, '')
    this.currentSelectionStage = 2
  }

  selectedTeacherType (): void {
    history.pushState({ entitySelectionStage: 3 }, '')
    this.currentSelectionStage = 3
  }

  selectedClassroomType (): void {
    history.pushState({ entitySelectionStage: 4 }, '')
    this.currentSelectionStage = 4
  }
}
</script>
