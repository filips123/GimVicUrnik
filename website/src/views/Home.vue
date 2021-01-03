<template>
  <loading />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import Loading from '@/components/base/Loading.vue'
import router from '@/router'
import { SettingsModule } from '@/store/modules/settings'

@Component({
  components: { Loading }
})
export default class Home extends Vue {
  created (): void {
    let isEntitySelected: boolean

    try {
      isEntitySelected = !!SettingsModule.selectedEntity
    } catch {
      isEntitySelected = false
    }

    // Redirect user either to timetable or welcome page
    if (isEntitySelected) {
      router.replace({ name: 'timetable' })
    } else {
      router.replace({ name: 'welcome' })
    }
  }
}
</script>
